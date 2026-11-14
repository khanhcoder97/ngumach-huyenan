"""Authoring timelines for twelve skills. Never gameplay events or approval."""
import argparse,json
from inspect_actor_library import ART,RUN

def build():
    records={r['id']:r for r in json.loads((ART/'generation_records.json').read_text(encoding='utf8'))}
    def track(id,component,start,duration,anchor='CASTER',forward=0,side=0,elevation=-65,size=96,rotation='FACING',angle=0,loop=False,z=2,optional=False,resource=False,screenX=0):
        r=records[component];seconds=r.get('previewDurationSeconds',.2 if component=='sk_mk_03_arc_component' else None)
        assert seconds and r.get('componentOnly')
        return dict(Id=id,ComponentId=component,Start=start,Duration=duration,SourceSeconds=seconds,Loop=loop,Anchor=anchor,
                    Forward=forward,Side=side,ScreenX=screenX,Elevation=elevation,Size=size,Rotation=rotation,Angle=angle,Z=z,
                    LowFxOptional=optional,ResourceInstances=resource,DepthByFacing=True,**({'ResourceRadius':34} if resource else {}))
    def variant(id,name,duration,tracks,dash=None,override=None,note='Mốc sự kiện là ví dụ xem art; không xác nhận hành vi server.'):
        return dict(Id=id,Name=name,Duration=duration,Tracks=tracks,DashStart=(dash or [0,0,0])[0],DashDuration=(dash or [0,0,0])[1],DashDistance=(dash or [0,0,0])[2],
                    OverrideClip=(override or ['',0])[0],OverrideStart=(override or ['',0])[1],Note=note)
    profiles=[]
    def profile(prefix,n,name,variants):
        profiles.append(dict(Id=f'SK_{prefix}_{n:02}',Name=name,ActorId='CLASS_MINH_KIEM' if prefix=='MK' else 'CLASS_ANH_DAO',
                             BodyClip=f'skill_{n:02}',TargetDistance=110,Variants=variants))
    t=track;v=variant
    guard=lambda end:t('guard','sk_mk_01_guard_ready_component',0,end,forward=24,elevation=-70,size=66,loop=True)
    profile('MK',1,'Phản Quang',[
        v('guard_timeout','Hết thế thủ, không phản kích',1.2,[guard(.4)]),
        v('counter_confirmed','Giả lập đỡ thành công',1.3,[guard(.18),t('parry','sk_mk_01_parry_component',.18,.4,forward=28,elevation=-70,size=74),t('counter','sk_mk_03_arc_component',.48,.2,forward=38,size=98)],override=['basic_attack',.28])])
    def thrust_tracks(end):return [t('aim','sk_mk_02_aim_component',0,.15,forward=45,elevation=-36,size=38),
        t('trail','sk_mk_02_trail_component',.15,.32,forward=-20,elevation=-22,size=110,z=0),
        t('stop','sk_mk_02_stop_dust_component',.35,.32,'END',elevation=-2,size=64,rotation='SCREEN',z=0)]
    profile('MK',2,'Tầm Long',[v('dash_end','Đường lướt minh họa',1.1,thrust_tracks(80),[.15,.2,80]),v('blocked_path','Điểm dừng sớm minh họa',1.1,thrust_tracks(35),[.15,.2,35])])
    profile('MK',3,'Kiếm Trận',[v('three_cuts','Ba nhịp riêng',1.1,[t('cut1','sk_mk_03_arc_component',0,.2,forward=34,size=92),t('cut2','sk_mk_03_arc_component',.12,.2,forward=34,size=92,angle=-35),t('cut3','sk_mk_03_arc_component',.26,.2,forward=34,size=115,angle=35)])])
    def shield_tracks(end,expiry):return [t('gain','sk_mk_04_gain_component',.2,.4,elevation=-34,size=84,rotation='SCREEN',z=0),
        t('hold','sk_mk_04_sustain_component',.6,end-.6,elevation=-34,size=84,rotation='SCREEN',loop=True,z=0),
        t('end','sk_mk_04_'+expiry+'_component',end,.32 if expiry=='break' else .4,elevation=-34,size=84,rotation='SCREEN',z=0)]
    profile('MK',4,'Thiết Y',[v('shield_expire','Khiên hết hạn tự nhiên',4.9,shield_tracks(4.2,'expire')),v('shield_break','Khiên bị phá minh họa',2.2,shield_tracks(1.4,'break'))])
    step=lambda:t('trail','sk_mk_05_trail_component',.08,.16,forward=-24,elevation=-12,size=108,z=0)
    profile('MK',5,'Bạch Hồng',[v('dash_end','Lướt không sát thương',.96,[step()],[.08,.16,80]),v('blocked_path','Dừng sớm không impact',.96,[step()],[.08,.16,35])])
    profile('MK',6,'Vạn Tượng Quy Nhất',[v('release','Tụ lực → phát kiếm → tan',2.05,[t('charge','sk_mk_06_charge_component',0,.7,forward=24,elevation=-48,size=64),t('cut','sk_mk_06_cut_component',.7,.35,forward=65,elevation=-32,size=190)])])
    bleed=t('bleed','sk_ad_01_bleed_status_component',.24,4,'TARGET_HP',size=21,rotation='SCREEN',elevation=-104,loop=True,screenX=30)
    cut=t('cut','sk_ad_01_cut_component',.12,.32,forward=36,size=96)
    profile('AD',1,'Huyết Nguyệt',[v('hit_status','Giả lập trúng và có trạng thái',4.8,[cut,bleed]),v('miss','Không gắn trạng thái',1.2,[cut])])
    mark=lambda duration:t('mark','sk_ad_02_mark_component',.24,duration,'TARGET',size=78,rotation='SCREEN',elevation=-2,loop=True,z=0)
    profile('AD',2,'Tàn Hỏa',[v('mark_expire','Dấu hết hạn, không nổ',5.95,[mark(5),t('expire','sk_ad_02_expire_component',5.24,.32,'TARGET',size=78,rotation='SCREEN',elevation=-2,z=0)]),
        v('mark_trigger','Giả lập đòn kế kích dấu',2,[mark(1),t('pop','sk_ad_02_pop_component',1.24,.4,'TARGET',size=102,rotation='SCREEN',elevation=-8)]),
        v('mark_cancel','Gỡ dấu sớm, không nổ',1.9,[mark(.76),t('expire','sk_ad_02_expire_component',1,.32,'TARGET',size=78,rotation='SCREEN',elevation=-2,z=0)])])
    profile('AD',3,'Xích Ảnh',[v('two_cuts','Hai cung thuận–ngược',1.2,[t('first','sk_ad_03_first_cut_component',.14,.2,forward=34,size=96),t('reverse','sk_ad_03_reverse_cut_component',.32,.2,forward=34,size=96)],[.14,.1,20])])
    down=t('down','sk_ad_04_down_cut_component',.2,.32,'TARGET',size=82,rotation='SCREEN',elevation=-3)
    profile('AD',4,'Tước Mạch',[v('slow_expire','Giả lập chậm rồi hết hạn',3.65,[down,t('slow','sk_ad_04_slow_mark_component',.36,2.5,'TARGET',size=72,rotation='SCREEN',elevation=-2,loop=True,z=0),t('expire','sk_ad_04_expire_component',2.86,.4,'TARGET',size=72,rotation='SCREEN',elevation=-2,z=0)]),v('boss_status','Không gắn dấu chậm',1.2,[down],note='Ví dụ boss không có dấu chậm; không xác nhận damage/Choáng Mạch.')])
    profile('AD',5,'Ảnh Bộ',[v('dash_end','Khói lướt, không tạo impact',1,[t('smoke','sk_ad_05_smoke_component',.08,.46,forward=-20,elevation=-8,size=108,z=0)],[.08,.22,80])])
    profile('AD',6,'Tử Diệm',[v('release','Tụ lực → quét thấp → cánh than',1.7,[t('charge','sk_ad_06_charge_component',0,.55,forward=14,elevation=-48,size=66),t('sweep','sk_ad_06_sweep_component',.55,.48,elevation=-4,size=164,rotation='SCREEN',z=0),t('petal','sk_ad_06_heat_petal_component',.8,.4,elevation=-4,size=26,rotation='SCREEN',optional=True,resource=True)])])
    assert len(profiles)==12 and sum(len(p['Variants']) for p in profiles)==20
    return dict(SchemaVersion=1,Scope='PRESENTATION_ASSEMBLY_REVIEW_ONLY',ProductionApproved=False,
        SourcePolicy='Original16pose PNGs, separate body/component clocks, no painted substitutes or pose padding.',
        Units='Visual authoring pixels at nominal140px actor height, not WU/metres/collision.',
        Sources=['docs/production/Skill_VFX_Cards_v1_vi.md','docs/production/Combat_Skills_VFX_Animation_Spec_vi.md','docs/production/Actor_Batch_20261113c_vi.md','docs/production/Actor_Batch_20261113d_vi.md','docs/production/Actor_Batch_20261113f_vi.md','docs/production/Actor_Batch_20261113g_vi.md'],Profiles=profiles)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();value=json.dumps(build(),ensure_ascii=False,indent=2)+'\n'
    for path in (ART/'skill_assembly_profiles_v1.json',RUN/'skill_assemblies.json'):
        if args.check:assert path.read_text(encoding='utf8')==value,'stale assembly authoring data: '+str(path)
        else:path.write_text(value,encoding='utf8')
    print(json.dumps(dict(profiles=12,scenarios=20,productionApproved=False)))
