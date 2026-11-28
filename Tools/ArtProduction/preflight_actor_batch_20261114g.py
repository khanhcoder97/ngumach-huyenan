"""Read original PNGs and report geometry/alpha; never edits raster or approves art."""
import json
from PIL import Image
from inspect_actor_library import ART,ROOT,inspect

def preflight():
    manifest=json.loads((ART/'Candidates_20261114g/candidate_manifest.json').read_text(encoding='utf8'))
    results=[]
    for source in manifest['records']:
        record=dict(source)
        if record.get('componentOnly'):
            record.update(layout='VISUALLY_VERIFIED_UNIFORM_GRID',layoutReviewNote='Original atlas manually viewed as four rows/four columns; this does not waive crop, alpha, duplicate or native review.')
        with Image.open(ART/record['source']) as image:
            alpha=image.getchannel('A');histogram=alpha.histogram()
            result=dict(id=record['id'],source=record['source'],mode=image.mode,size=list(image.size),alphaZeroPixels=histogram[0],alphaNonSolidPixels=sum(histogram[1:200]),alphaSolidPixels=sum(histogram[200:]),cornerAlpha=[image.getpixel(p)[3] for p in [(0,0),(image.width-1,0),(0,image.height-1),(image.width-1,image.height-1)]])
        try:
            page=inspect(record)
            result.update(geometryReady=True,sourceFrames=page['sourceFrames'],sha256=page['sha256'])
        except (AssertionError,OSError) as error:
            result.update(geometryReady=False,reason=str(error))
        results.append(result)
    output=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114g'
    output.mkdir(parents=True,exist_ok=True)
    report=dict(scope='READ_ONLY_GEOMETRY_NOT_NATIVE_OR_VISUAL_ACCEPTANCE',selected=len(results),geometryReady=sum(r['geometryReady'] for r in results),rasterModified=False,entries=results)
    (output/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='entries'}))
    for result in results:
        if not result['geometryReady']:print(json.dumps(result))

if __name__=='__main__':preflight()
