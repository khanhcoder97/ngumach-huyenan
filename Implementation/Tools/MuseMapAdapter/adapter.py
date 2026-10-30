"""OPC-12: validated, review-only bridge from Muse layouts to world coordinates."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import sys

CODE_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(CODE_ROOT))
from Implementation.Asset_Handoff.png_validation import validate_png, PNGValidationProblem
from Implementation.Tools.ContentPipeline.compiler import canonical_bytes
from Implementation.Tools.ContentPipeline.compiler_core import source_bytes
from Implementation.Tools.ContentPipeline.validation import load_json_file
from Tools.AssetPreview.server import calculate_layout
from Implementation.Tools.json_schema import validate as validate_schema

MANIFEST = 'docs/production/World_Spawn_Gathering_Manifest_vi.csv'
ASSETS = 'Client/Assets/ArtManifests/muse_delivery_manifest.json'


def schema_check(value, filename):
    schema = load_json_file(Path(__file__).with_name('schemas') / filename,'adapter schema')
    errors = []
    validate_schema(value,schema,'map',errors)
    if errors:
        raise ValueError('; '.join(errors))


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def safe_file(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative or PureWindowsPath(relative).drive:
        raise ValueError('source path must be a portable repository-relative path')
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('source path traversal/absolute path is forbidden')
    result = (root / p).resolve()
    if not result.is_relative_to(root) or not result.is_file():
        raise ValueError('missing source or path outside root: ' + relative)
    return result


def keys(value, allowed, required=()):
    if not isinstance(value, dict) or set(value) - set(allowed) or set(required) - set(value):
        raise ValueError('invalid object fields; allowed=' + ','.join(allowed))


def integer(value, minimum=0, maximum=1_000_000):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('integer outside supported bounds')
    return value


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 10_000_000:
        raise ValueError('coordinate must be finite and bounded')
    return value


def unique(values, key):
    result = {}
    for value in values:
        name = value.get(key)
        if not isinstance(name, str) or not name or name in result:
            raise ValueError('duplicate/missing ' + key)
        result[name] = value
    return result


def build(layout, root=CODE_ROOT, asset_manifest=ASSETS):
    root = Path(root).resolve()
    schema_check(layout,'layout_input.schema.json')
    keys(layout, ['schemaVersion','mapId','layoutVersion','synthetic','tilePixels','pixelsPerUnit',
                  'originWu','rowAxis','tilesets','layers','props','placementOverrides','actorAssets'],
         ['schemaVersion','mapId','layoutVersion','synthetic','tilePixels','pixelsPerUnit','originWu',
          'rowAxis','tilesets','layers','props','placementOverrides','actorAssets'])
    if type(layout['schemaVersion']) is not int or layout['schemaVersion'] != 1:
        raise ValueError('unsupported layout version')
    if not isinstance(layout['mapId'], str) or not layout['mapId'].startswith('MAP_'):
        raise ValueError('invalid mapId')
    if not isinstance(layout['layoutVersion'], str) or not layout['layoutVersion']:
        raise ValueError('layoutVersion is required')
    if type(layout['synthetic']) is not bool:
        raise ValueError('synthetic must be boolean')
    if type(layout['tilePixels']) is not int or layout['tilePixels'] != 16 or type(layout['pixelsPerUnit']) is not int or layout['pixelsPerUnit'] != 20:
        raise ValueError('baseline requires tile16px at20PPU')
    if layout['rowAxis'] not in ['+Y','-Y']:
        raise ValueError('rowAxis must explicitly be +Y or -Y')
    keys(layout['originWu'], ['x','y'], ['x','y'])
    ox, oy = number(layout['originWu']['x']), number(layout['originWu']['y'])
    for field in ['tilesets','layers','props','placementOverrides','actorAssets']:
        if not isinstance(layout[field], list) or len(layout[field]) > 10000:
            raise ValueError(field + ' must be a bounded array')

    bounds_path = safe_file(root, 'Implementation/Content/map_bounds.json')
    bounds = load_json_file(bounds_path,'map bounds')
    if layout['mapId'] not in bounds['knownMapIds']:
        raise ValueError('unknown canonical mapId')
    sources = []
    tilesets = []
    for tile in layout['tilesets']:
        keys(tile, ['id','image','sourceRef'], ['id','image','sourceRef'])
        if not isinstance(tile['sourceRef'], str) or not tile['sourceRef']:
            raise ValueError('tileset sourceRef is required')
        path = safe_file(root, tile['image'])
        info = validate_png(path)
        if info.width % 16 or info.height % 16:
            raise ValueError('tileset dimensions must be multiples of16px')
        tilesets.append({**tile, 'pixelWidth':info.width, 'pixelHeight':info.height,
                         'columns':info.width//16, 'rows':info.height//16,
                         'sha256':digest(path.read_bytes())})
        sources.append({'path':tile['image'], 'sha256':digest(path.read_bytes()), 'normalization':'BINARY'})
    tile_by_id = unique(tilesets, 'id')
    layers = []
    shape = None
    for layer in layout['layers']:
        keys(layer,['id','role','tilesetId','width','height','tiles'],['id','role','tilesetId','width','height','tiles'])
        if layer['role'] not in ['GROUND','DECORATION','COLLISION_CANDIDATE']:
            raise ValueError('unsupported layer role')
        width,height = integer(layer['width'],1,4096),integer(layer['height'],1,4096)
        if width*height > 1_000_000 or not isinstance(layer['tiles'],list) or len(layer['tiles']) != width*height:
            raise ValueError('layer dimensions/count exceed budget or disagree')
        if shape is not None and shape != (width,height):
            raise ValueError('all layers must share grid dimensions')
        shape = width,height
        tile = tile_by_id.get(layer['tilesetId'])
        if tile is None:
            raise ValueError('layer refers to unknown tileset')
        for value in layer['tiles']:
            integer(value,0,tile['columns']*tile['rows'])
        layers.append(dict(layer))
    unique(layers,'id')
    if not layers:
        raise ValueError('at least one layer is required')
    width,height = shape
    sign = 1 if layout['rowAxis']=='+Y' else -1
    props = []
    for prop in layout['props']:
        keys(prop,['id','tilesetId','tileId','column','row'],['id','tilesetId','tileId','column','row'])
        tile = tile_by_id.get(prop['tilesetId'])
        if tile is None:
            raise ValueError('prop refers to unknown tileset')
        tile_id = integer(prop['tileId'],1,tile['columns']*tile['rows'])
        column,row = integer(prop['column'],0,width-1),integer(prop['row'],0,height-1)
        index=tile_id-1
        props.append({**prop,'positionWu':{'x':ox+(column+0.5)*0.8,'y':oy+sign*(row+0.5)*0.8},
                      'pivot':'bottom_center', 'pixelRectTopLeft':{'x':(index%tile['columns'])*16,
                      'y':(index//tile['columns'])*16,'width':16,'height':16}})
    unique(props,'id')

    csv_path=safe_file(root,MANIFEST)
    with csv_path.open(encoding='utf-8-sig',newline='') as f:
        canonical=list(csv.DictReader(f))
    records=unique(canonical,'record_id')
    selected={k:r for k,r in records.items() if r['map_id']==layout['mapId']}
    if not selected:
        raise ValueError('map has no canonical placement records')
    overrides=unique(layout['placementOverrides'],'originalRecordId')
    for key,override in overrides.items():
        keys(override,['originalRecordId','xWu','yWu','reason'],['originalRecordId','xWu','yWu','reason'])
        if key not in selected:
            raise ValueError('placement override is unknown or belongs to another map')
        number(override['xWu']);number(override['yWu'])
        if not isinstance(override['reason'],str) or not override['reason'].strip():
            raise ValueError('migration candidate requires a reason')
    placements=[]
    findings=[]
    for record_id,record in sorted(selected.items()):
        original={'x':number(float(record['x_wu'])),'y':number(float(record['y_wu']))}
        override=overrides.get(record_id)
        target=original if override is None else {'x':override['xWu'],'y':override['yWu']}
        placements.append({'originalRecordId':record_id,'originalRecord':record,
                           'originalXYWu':original,'candidateXYWu':dict(target),
                           'migrationState':'TOPDOWN_REVIEW_REQUIRED',
                           'reason':override['reason'] if override else 'Original placement retained; no migration approved'})
        x2,y2=ox+width*0.8,oy+sign*height*0.8
        if not min(ox,x2)<=target['x']<=max(ox,x2) or not min(oy,y2)<=target['y']<=max(oy,y2):
            findings.append({'recordId':record_id,'code':'OUTSIDE_CANDIDATE_LAYOUT'})

    manifest_path=safe_file(root,asset_manifest)
    manifest=load_json_file(manifest_path,'asset manifest')
    assets=unique(manifest['assets'],'assetId')
    actors=[]
    if any(not isinstance(x,str) for x in layout['actorAssets']) or len(layout['actorAssets']) != len(set(layout['actorAssets'])):
        raise ValueError('duplicate actor reference')
    for actor_id in layout['actorAssets']:
        asset=assets.get(actor_id)
        if asset is None:
            raise ValueError('missing actor asset: '+str(actor_id))
        resolved=calculate_layout(asset,manifest.get('manifestVersion',1))
        if not resolved.get('supported'):
            raise ValueError('unsupported actor geometry: '+str(actor_id))
        path=safe_file(root,asset['path']);info=validate_png(path)
        if (info.width,info.height)!=(asset['pixelWidth'],asset['pixelHeight']) or asset.get('pixelsPerUnit')!=20:
            raise ValueError('actor image dimensions/PPU differ from manifest')
        if resolved['grid']['rows']!=8 or set(asset['directions'])!={'N','NE','E','SE','S','SW','W','NW'}:
            raise ValueError('actor must provide eight explicit directional rows')
        if asset.get('pivot')!='bottom_center':
            raise ValueError('actor requires explicit bottom_center pivot')
        frame_width,frame_height=resolved['frameSize']['width'],resolved['frameSize']['height']
        frames=[{'direction':direction,'column':column,
                 'pixelRectTopLeft':{'x':column*frame_width,'y':row*frame_height,'width':frame_width,'height':frame_height},
                 'pixelRectUnity':{'x':column*frame_width,'y':info.height-(row+1)*frame_height,'width':frame_width,'height':frame_height}}
                for row,direction in enumerate(asset['directions']) for column in range(resolved['grid']['cols'])]
        actors.append({'assetId':actor_id,'path':asset['path'],'status':asset['status'],
                       'pivot':asset.get('pivot'),'geometry':resolved,'frames':frames,
                       'sha256':digest(path.read_bytes()),'engineImport':'UNVERIFIED'})
        sources.append({'path':asset['path'],'sha256':digest(path.read_bytes()),'normalization':'BINARY'})
        if asset['status']!='approved':findings.append({'assetId':actor_id,'code':'ART_NOT_APPROVED'})
    for relative in [MANIFEST,asset_manifest,'Implementation/Content/map_bounds.json']:
        sources.append({'path':relative,'sha256':digest(source_bytes(safe_file(root,relative).read_bytes())),
                        'normalization':'UTF8_NO_BOM_LF'})
    result={'schemaVersion':1,'mapId':layout['mapId'],'layoutVersion':layout['layoutVersion'],
            'status':'CANDIDATE_REQUIRES_REVIEW','synthetic':layout['synthetic'],
            'runtimeActivationAllowed':False,'navigationReview':'TOPDOWN_REVIEW_REQUIRED',
            'tilePixels':16,'pixelsPerUnit':20,'worldCellSizeWu':0.8,
            'originWu':layout['originWu'],'rowAxis':layout['rowAxis'],
            'layoutDigest':digest(canonical_bytes(layout)),
            'canonicalPlacementCount':len(canonical),'mapPlacementCount':len(placements),
            'tilesets':tilesets,'layers':layers,'props':props,'placements':placements,
            'actors':actors,'sources':sorted(sources,key=lambda x:x['path']),'findings':findings}
    result['bundleDigest']=digest(canonical_bytes(result))
    schema_check(result,'map_candidate.schema.json')
    return result
