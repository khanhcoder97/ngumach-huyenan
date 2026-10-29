# Âm thanh Ngũ Mạch — thiết kế và danh mục sản xuất v1

Codex phụ trách sound direction/cue mapping và review tích hợp. Gói này là thiết kế có dữ liệu, **chưa có clip nhạc/SFX/voice được tạo hoặc nhập Unity**. Muse vẫn phụ trách stems/subtitle/video theo cinema pack; không giao Muse tự sáng tác toàn bộ audio gameplay ngoài hàng đợi đã nhận.

Catalogue: `Implementation/Content/DesignBaselines/audio_cues_v1.json`. 30cue kỹ năng dùng đúng soundKey đã giao trong skill_vfx_art_v1;33cue dùng chung cho combat/UI/world/boss/ambience/music. Mọi clip/source/license còn `null`, assetState MISSING. Không đưa catalogue này vào runtime loader hoặc manifest ảnh của Muse.

## 1. Bản sắc và khoảng lặng

| Môn phái | Chất liệu âm | Nhịp nhận diện | Tránh |
|---|---|---|---|
| Minh Kiếm | cạnh kim loại khô, tiếng ngân ngắn như phiến đồng mỏng | đầu rõ, ngừng sạch, ba nhát nặng dần | tiếng kiếm dài chói liên tục; parry clang khi chỉ cast guard |
| Ảnh Đao | gió qua vải, tiếng than lách tách nhỏ và lưỡi đao trầm | hai nhịp ngắn, đuôi tắt gấp | lửa gầm phủ kín mọi kỹ năng; tiếng máu/bạo lực tả thực |
| Huyền Bút | nét bút trên giấy, nước chạm men, hơi thở nước mảnh | đưa–buông–ngừng; hồi máu dịu, không giống impact | tiếng bong bóng lặp không ngừng; heal sáng gắt hơn cảnh báo boss |
| Thạch Chùy | gỗ trầm, phiến đá nứt, cát rơi | có trọng lượng nhưng attack rõ trước đuôi trầm | chỉ dùng sub-bass khiến loa điện thoại mất tín hiệu |
| Linh Cung | dây bật, gió qua lá, âm sáo ngắn không thành giai điệu | nhiều phát tách nhau, đuôi nhẹ | một tiếng nổ lớn thay cả năm tên; hú rồng cho mọi đạn Mộc |

Nhạc lấy cảm hứng từ vật liệu thủ công/sông nước của thế giới, giai điệu nguyên bản. Bến Mưa dùng một câu nhạc bỏ lửng; khi khám phá tiếng chuông, nhạc nhường chỗ để người chơi nghe phần đuôi bị thiếu. Thăng Long có nhiều lớp sinh hoạt nhưng không lặp tiếng người bán rõ thành lời mỗi vài giây. Khám phá cần có im lặng, không chèn fanfare mỗi lần nhặt vật chứng.

## 2. Cue phát khi nào

- UI focus/open/click là presentation local; không đồng nghĩa giao dịch thành công. Quest complete/grant, hurt/death/heal/impact phải đợi authoritative event/state tương ứng.
- Skill `soundKey` là semantic reference, chưa là event wire hoặc path file. Adapter cần mapping theo version, castId/eventId/hitIndex/status revision. Không phát SFX impact từ input hoặc `combat.effect` một bước hiện tại.
- Phản Quang: guard có tiếng chuyển thế nhỏ nếu sau này bổ sung cue; `metal_parry` chỉ phát khi counter confirmed. Cửa guard hết mà không bị đánh không có tiếng đỡ chuẩn.
- Kiếm Trận: hit0/1/2 dùng variation nhẹ/vừa/nặng, theo từng hit event. Không phát clip ba nhát đầy đủ mỗi lần nhận một event trong ba nhát. Liên Châu theo từng lần bắn xác nhận, không phát năm âm đồng thời từ một frame.
- Khiên/mark/trap: một tiếng apply; refresh chỉ cập nhật state, không phát lại apply như buff mới. Loop nếu có phải là component riêng, dừng ở status end/cancel/despawn/map change; CAST_END không tự kết thúc status còn sống.
- Dây Gai đặt bẫy và trap trigger khác nhau; không phát tiếng gây damage ngay khi đặt. Hồi phục AoE không phát một fanfare cho từng đồng đội; cùng cast lấy một cue tại vùng và các tick nhỏ đã giới hạn.
- Dash chỉ whoosh khi đường đi được xác nhận; tường cắt ngắn không phát impact trúng địch nếu không có hit event. Spell miss/immune không dùng âm crit hoặc tiếng giết quái.
- Retry/dedupe: `(mapInstanceId,eventId,cueKey,hitIndex)` chỉ phát một lần. Reconnect dựng lại loop đang active từ state, không replay hit/fanfare cũ. Không nghe actor khác instance hoặc ngoài visibility/audience policy để tránh lộ mục tiêu.

## 3. Mixer, giới hạn và khả năng nghe

Baseline theo Rules §8: Master/Music/Ambience/SFX/UI, gain0..1. Mute giữ gain đã lưu, không ép bật tiếng cảnh báo khi người chơi tắt âm. Giữ visual/text tương đương cho mọi tín hiệu quan trọng.

| Nhóm voice | Cap | Priority baseline | Quy tắc |
|---|---:|---:|---|
| footstep |8|20|distance/contact trên vật liệu thật; không suy từ mỗi packet move |
| hit |16|60|ưu tiên self/target gần; bớt hit nền trước warning |
| skill |12|70|mỗi cue tối đa2instance đồng thời, cắt voice cũ thấp nhất khi cần |
| UI |4|80|focus min gap80ms; không dồn hàng chục beep khi focus đổi nhanh |
| ambience |4|10|stream/tile layer có crossfade và unload, không4lớp cho mỗi chunk |
| music |2|30|tối đa hai track đang crossfade, không cộng mỗi vùng thành một bài |
| boss warning |dùng budget skill, được ưu tiên100|100|steal voice skill thấp, không mở budget vô hạn |

Cap theo category và per-cue cùng có hiệu lực. Voice stealing chọn priority thấp nhất, rồi voice cũ nhất; loop dừng có fade ngắn tránh click. Warning ưu tiên trong ngân sách, không vượt mute và không ép âm lượng nguy hiểm. Đề xuất tuning v1: duck Music/Ambience còn50% trong cảnh báo, attack80ms/hold200ms/release350ms; đây chưa là kết quả đo thiết bị.

Spatial là mặt phẳngXY; khoảng cách WU chuyển đúng một lần. Cue skill thường min4/max28WU theo catalogue, không pan theo worldZ. Âm UI/nhạc là2D. Critical boss cue chỉ gửi cho audience encounter hoặc người thật sự bị ảnh hưởng; không phát toàn server. Camera HUB_WIDE không tăng cự ly nghe hoặc volume để lộ actor xa.

## 4. Ba cảnh báo Mãng Cốt

1. Quét thân: tiếng vỏ xương cọ thấp và rít ngắn, bắt đầu cùng cone telegraph0,9s. Có nét mid-range nghe được trên loa nhỏ; không dùng tiếng còi UI.
2. Lặn/trồi: hai tiếng áp nước cách nhau, nền hút nhẹ khi chốt target rồi cue trồi tại hit server; warning1,2s không phải impact phát sớm. Đồ họa/text giữ điểm nhắm khi mute.
3. Vòng bọt: chuỗi ba bọt ngắn có khoảng nghỉ, khớp annulus3..7WU báo1s. Không dùng cùng tiếng trồi làm người chơi nhầm hai cơ chế.

Những tiếng hit/end riêng chỉ phát khi server cho biết kết quả; clip warning cần có stop/cancel point. Pha transition không replay toàn bộ intro nhạc nếu encounter chưa reset attempt.

## 5. Sản xuất và bàn giao

SFX master WAV PCM48kHz/24bit; export đề xuất48kHz/16bit mono cho spatial, stereo cho UI cần thiết. Music/ambience master stereo48kHz, runtime OGG streaming thử nghiệm; chưa đặt compression/import settings vào asset chưa tồn tại. Không gọi bitrate đề xuất là mobile memory benchmark.

Mỗi cue giao source/session chỉnh sửa được hoặc quy trình synthesis, variations, clip thật, sample rate/channels/length/loop points, peak/loudness measurement, ownership/license và SHA. File thiếu source/provenance không được tự điền `original`. Không lấy sample từ JAR hoặc tách âm của video tham khảo.

Một cue có nhiều clip dùng stable variationId và deterministic/no-immediate-repeat policy; seed presentation không ảnh hưởng RNG damage/loot. Stem cinema do Muse giao có sidecar theo #29, không âm thầm sửa sprite manifest schema để nhét audio kind. Audio delivery schema/loader cần proposal tích hợp riêng trước runtime.

## 6. Nghiệm thu

- Nghe mono/stereo, tai nghe và loa điện thoại; bước chân không lấn warning, voice limit giữ ổn khi10người spam skill. Chụp profiler/audio voice count và ghi build/device.
- Mute từng bus rồi master: gameplay vẫn đủ visual, đổi map không sống lại loop; gain cũ phục hồi khi unmute.
- Retry/duplicate/out-of-order/reconnect không nhân tiếng, end loop không đến trước apply mới hơn, pool reuse không mang clip của actor cũ.
- Xác nhận guard hụt/đặt bẫy/heal/taunt không phát âm trúng/sát thương giả. Test cả giao tranh và60–120s khám phá yên sau boss.
- Review bằng clip thật có comparison mix; catalogue PASS chỉ chứng minh key/ref/budget, không chứng minh âm thanh hay, license đã cleared hoặc đã có audio asset.

Thứ tự tiếp theo của Codex: review thư viện cue và pipeline trigger trên client sau server lifecycle; tạo/nhận lô âm mẫu nguyên bản và đo trên thiết bị trước nhân rộng. Không đóng CX-04 chỉ vì đã có63dòng danh mục.
