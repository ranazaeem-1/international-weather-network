# GWN vs IWN: North Carolina nor'easter footage (20 Oct 2026)

The forensic run was stopped early at the user's request. Numbers below are what was measured. "Untraced" means *not yet matched*; it is **not** proof that a shot comes from this storm.

Evidence (scratchpad `cmp_nc\`):
- `ev\gwnsep_a.jpg`: GWN shots next to the matching footage in GWN's own September videos.
- `ev\yt_matches.jpg`: GWN shots next to the matching older YouTube uploads.
- `ev\E_manwading_viralhog.jpg`: the "man wading" clip matched to ViralHog.
- `pool_summary.json`: per-video counts of new and recycled footage.

## 1. Quantity: GWN does not have more footage

GWN published 6 North Carolina videos on 18–19 Oct (wNCDK-l0oBw, m-tpSSrVTvc, YLkEjNJHoJQ, P_6RvYzR6cY, 8BQBdn4FCyk, cFZ6tOullGA): **99.5 min in total**.

| Video | Length (min) | Shots | New footage (min) | Recycled from earlier NC videos |
|---|---|---|---|---|
| wNCDK-l0oBw | 12.1 | 77 | 11.7 | 3% |
| m-tpSSrVTvc | 15.1 | 92 | 2.3 | 84% |
| YLkEjNJHoJQ | 18.1 | 117 | 0.9 | 95% |
| P_6RvYzR6cY | 20.1 | 133 | 0.8 | 96% |
| 8BQBdn4FCyk | 22.1 | 147 | 0.5 | 98% |
| cFZ6tOullGA | 12.1 | 76 | 0.1 | 100% |

- **GWN pooled:** about 16.3 min of distinct footage, 126 distinct shots.
- **IWN's Outer Banks draft:** 15.7 min of distinct footage, 77 clips (81 shots), median shot 12.8 s.

That is **the same amount of footage**. GWN re-cut one library into six videos.

## 2. Quality: about half of GWN's best scenes are from earlier storms

At least **59 of GWN's 126 distinct shots (47%)** match footage that was published *before this storm began* (16 Oct):

| Source GWN reused | Published | What it is |
|---|---|---|
| GWN's own videos (3_UdHwx5Q2g, XQLImnJG4wQ, z40Etx7MqKA, YINrD6007Tg, GV2F286IK1w, J_YgKLOLxmo, i8LYD_HJVUc, zO3JjQX1lGI, EF7GXcs8eXM) | 26–30 Sep 2026 | Late-September nor'easter (NC 12 washout on Pea Island) |
| FOX Weather 7sp6pQVVF_0; USA TODAY 7xW3Vbtf7Do and vwdPOz0Cq_I; ABC 7 Chicago kuk4qcr8sPM | 24–25 Sep 2026 | September nor'easter, from TV and news outlets |
| CRISIS REPORT G9kimv0PiXU; Disasters Watch dVGJ8SpxBiY | 25–26 Sep 2026 | Compilations of the September storm |
| 13News Now V6H-3UGpMCc ("Raw video: OBX houses collapse"); New York Post FdREoPZiCI4 | 2–4 Feb 2026 | February 2026 Buxton house collapses |
| ViralHog qMKfffEZPVk ("Nor'easter Hammers Cape Hatteras") | 9 Oct 2026 | Licensed viral clip that predates this storm |

- **The scenes:** these are the stilt houses with surf underneath, the car buried in sand, the flooded street with a school bus, the houses collapsing and the man wading.
- **GWN's own disclosure:** its first NC video (wNCDK at 1:02) carries a "VIEWER ADVISORY — Some footage in this video is from previous nor'easter events and may not depict current conditions" banner.
- **Untraced:** the other 67 distinct shots were not matched before the run was stopped.

## 3. Why IWN ends up with webcams for a storm like this

1. **Verification rule.** IWN only uses footage proven to be from the current event. GWN's most dramatic material fails that test: it is the September storm and the February collapses.
2. **No TV or news footage.** GWN reuses FOX Weather, USA TODAY and ABC footage. IWN's rule excludes it.
3. **No X, TikTok or Facebook search.** Most fresh eyewitness video of a storm like this is posted there, not on YouTube. The agents cannot search X, because the browser is not logged in and Claude does not log in. On 18–19 Oct YouTube had almost no raw footage of this storm apart from livestreamed webcams.
4. **The fix that worked:** for the Spain update, the user's 25 X links gave 22 strong verified clips. That is how IWN closes the eyewitness gap.

## 4. Options (for the user to decide)

- **A. Labelled archive footage in history chapters.** Show the February collapses or the September washout *only* where the script talks about them, with an on-screen "ARCHIVE · FEB 2026" tag. This is honest, and it adds GWN's drama without passing old footage off as current.
- **B. X sourcing.** Either the user keeps sending X links, which was the best result so far, or the user logs in to X in the built-in browser themselves so agents can run X "Latest" searches.
- **C. One library per event, several videos.** GWN made 6 videos from 16 min of footage. IWN could publish a Day 1 and a Day 2 video from one harvest.
- **D. Keep the current rule unchanged.** Weak events then stay webcam-heavy, as the Outer Banks draft is.

**Not recommended:** presenting old footage as current, which is what GWN's small disclaimer stands in for.

**Decision (user, 20 Oct 2026):** archive footage is allowed, but only in chapters about the past event, with narration that says when it happened. There is no on-screen tag. The rule is in `worflow.md` §0 and in the pipeline as `E.build(archive=...)`.


## 5. Every traced moment, with links (GWN's first NC video `wNCDK-l0oBw`)

Click the GWN time to see the shot, then the source link to see the same footage published earlier. Every pair was checked visually. The same shots repeat in GWN's 5 later NC videos (m-tpSSrVTvc, YLkEjNJHoJQ, P_6RvYzR6cY, 8BQBdn4FCyk, cFZ6tOullGA). For example, the ABC jeep clip is at wNCDK 6:05, m-tpSSrVTvc 11:49, P_6RvYzR6cY 3:58, 8BQBdn4FCyk 15:56 and cFZ6tOullGA 6:48.

| GWN wNCDK-l0oBw | Same footage published earlier | Uploader | Published |
|---|---|---|---|
| [0:01](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=1s) | [V6H-3UGpMCc @ 0:23](https://www.youtube.com/watch?v=V6H-3UGpMCc&t=23s) | 13News Now | 02-02-2026 |
| [0:34](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=34s) | [FdREoPZiCI4 @ 1:01](https://www.youtube.com/watch?v=FdREoPZiCI4&t=61s) | New York Post | 04-02-2026 |
| [0:39](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=39s) | [dVGJ8SpxBiY @ 5:46](https://www.youtube.com/watch?v=dVGJ8SpxBiY&t=346s) | Disasters Watch  | 25-09-2026 |
| ″ | [i8LYD_HJVUc @ 5:05](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=305s) | Global Weather Network | 29-09-2026 |
| [0:45](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=45s) | [EF7GXcs8eXM @ 0:43](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=43s) | Global Weather Network | 30-09-2026 |
| [0:50](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=50s) | [EF7GXcs8eXM @ 0:47](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=47s) | Global Weather Network | 30-09-2026 |
| [1:02](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=62s) | [i8LYD_HJVUc @ 3:43](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=223s) | Global Weather Network | 29-09-2026 |
| [1:05](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=65s) | [z40Etx7MqKA @ 8:15](https://www.youtube.com/watch?v=z40Etx7MqKA&t=495s) | Global Weather Network | 27-09-2026 |
| [1:16](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=76s) | [GV2F286IK1w @ 5:03](https://www.youtube.com/watch?v=GV2F286IK1w&t=303s) | Global Weather Network | 28-09-2026 |
| ″ | [kuk4qcr8sPM @ 0:11](https://www.youtube.com/watch?v=kuk4qcr8sPM&t=11s) | ABC 7 Chicago | 24-09-2026 |
| [1:29](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=89s) | [z40Etx7MqKA @ 8:25](https://www.youtube.com/watch?v=z40Etx7MqKA&t=505s) | Global Weather Network | 27-09-2026 |
| [1:33](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=93s) | [7xW3Vbtf7Do @ 0:03](https://www.youtube.com/watch?v=7xW3Vbtf7Do&t=3s) | USA TODAY | 24-09-2026 |
| [1:39](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=99s) | [EF7GXcs8eXM @ 0:31](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=31s) | Global Weather Network | 30-09-2026 |
| [1:46](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=106s) | [G9kimv0PiXU @ 6:18](https://www.youtube.com/watch?v=G9kimv0PiXU&t=378s) | CRISIS REPORT | 26-09-2026 |
| [1:59](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=119s) | [J_YgKLOLxmo @ 25:07](https://www.youtube.com/watch?v=J_YgKLOLxmo&t=1507s) | Global Weather Network | 29-09-2026 |
| [2:04](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=124s) | [GV2F286IK1w @ 8:35](https://www.youtube.com/watch?v=GV2F286IK1w&t=515s) | Global Weather Network | 28-09-2026 |
| [2:22](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=142s) | [z40Etx7MqKA @ 11:27](https://www.youtube.com/watch?v=z40Etx7MqKA&t=687s) | Global Weather Network | 27-09-2026 |
| [2:37](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=157s) | [XQLImnJG4wQ @ 6:27](https://www.youtube.com/watch?v=XQLImnJG4wQ&t=387s) | Global Weather Network | 26-09-2026 |
| [2:40](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=160s) | [G9kimv0PiXU @ 2:43](https://www.youtube.com/watch?v=G9kimv0PiXU&t=163s) | CRISIS REPORT | 26-09-2026 |
| [2:48](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=168s) | [z40Etx7MqKA @ 3:01](https://www.youtube.com/watch?v=z40Etx7MqKA&t=181s) | Global Weather Network | 27-09-2026 |
| [2:54](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=174s) | [YINrD6007Tg @ 5:18](https://www.youtube.com/watch?v=YINrD6007Tg&t=318s) | Global Weather Network | 28-09-2026 |
| [3:03](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=183s) | [EF7GXcs8eXM @ 7:39](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=459s) | Global Weather Network | 30-09-2026 |
| [3:16](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=196s) | [GV2F286IK1w @ 20:41](https://www.youtube.com/watch?v=GV2F286IK1w&t=1241s) | Global Weather Network | 28-09-2026 |
| [3:24](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=204s) | [vwdPOz0Cq_I @ 0:18](https://www.youtube.com/watch?v=vwdPOz0Cq_I&t=18s) | USA TODAY | 25-09-2026 |
| [3:28](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=208s) | [3_UdHwx5Q2g @ 19:27](https://www.youtube.com/watch?v=3_UdHwx5Q2g&t=1167s) | Global Weather Network | 27-09-2026 |
| [3:34](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=214s) | [3_UdHwx5Q2g @ 19:33](https://www.youtube.com/watch?v=3_UdHwx5Q2g&t=1173s) | Global Weather Network | 27-09-2026 |
| [3:52](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=232s) | [YINrD6007Tg @ 7:09](https://www.youtube.com/watch?v=YINrD6007Tg&t=429s) | Global Weather Network | 28-09-2026 |
| [4:05](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=245s) | [i8LYD_HJVUc @ 3:18](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=198s) | Global Weather Network | 29-09-2026 |
| [4:24](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=264s) | [EF7GXcs8eXM @ 7:22](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=442s) | Global Weather Network | 30-09-2026 |
| [5:03](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=303s) | [J_YgKLOLxmo @ 3:21](https://www.youtube.com/watch?v=J_YgKLOLxmo&t=201s) | Global Weather Network | 29-09-2026 |
| [5:06](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=306s) | [G9kimv0PiXU @ 2:43](https://www.youtube.com/watch?v=G9kimv0PiXU&t=163s) | CRISIS REPORT | 26-09-2026 |
| ″ | [J_YgKLOLxmo @ 3:13](https://www.youtube.com/watch?v=J_YgKLOLxmo&t=193s) | Global Weather Network | 29-09-2026 |
| [5:14](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=314s) | [z40Etx7MqKA @ 1:31](https://www.youtube.com/watch?v=z40Etx7MqKA&t=91s) | Global Weather Network | 27-09-2026 |
| [5:15](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=315s) | [G9kimv0PiXU @ 5:13](https://www.youtube.com/watch?v=G9kimv0PiXU&t=313s) | CRISIS REPORT | 26-09-2026 |
| [5:16](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=316s) | [G9kimv0PiXU @ 5:14](https://www.youtube.com/watch?v=G9kimv0PiXU&t=314s) | CRISIS REPORT | 26-09-2026 |
| ″ | [z40Etx7MqKA @ 1:33](https://www.youtube.com/watch?v=z40Etx7MqKA&t=93s) | Global Weather Network | 27-09-2026 |
| ″ | [J_YgKLOLxmo @ 3:25](https://www.youtube.com/watch?v=J_YgKLOLxmo&t=205s) | Global Weather Network | 29-09-2026 |
| [5:18](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=318s) | [z40Etx7MqKA @ 1:35](https://www.youtube.com/watch?v=z40Etx7MqKA&t=95s) | Global Weather Network | 27-09-2026 |
| [5:22](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=322s) | [YINrD6007Tg @ 12:11](https://www.youtube.com/watch?v=YINrD6007Tg&t=731s) | Global Weather Network | 28-09-2026 |
| [5:25](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=325s) | [z40Etx7MqKA @ 5:13](https://www.youtube.com/watch?v=z40Etx7MqKA&t=313s) | Global Weather Network | 27-09-2026 |
| [5:38](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=338s) | [YINrD6007Tg @ 2:03](https://www.youtube.com/watch?v=YINrD6007Tg&t=123s) | Global Weather Network | 28-09-2026 |
| [5:41](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=341s) | [qMKfffEZPVk @ 0:02](https://www.youtube.com/watch?v=qMKfffEZPVk&t=2s) | ViralHog | 09-10-2026 |
| [5:51](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=351s) | [qMKfffEZPVk @ 0:14](https://www.youtube.com/watch?v=qMKfffEZPVk&t=14s) | ViralHog | 09-10-2026 |
| [5:54](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=354s) | [qMKfffEZPVk, man wading near the end](https://www.youtube.com/watch?v=qMKfffEZPVk&t=55s) | ViralHog | 09-10-2026 |
| [5:55](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=355s) | [YINrD6007Tg @ 2:33](https://www.youtube.com/watch?v=YINrD6007Tg&t=153s) | Global Weather Network | 28-09-2026 |
| [6:05](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=365s) | [Ik_ODHmycMc @ 0:03](https://www.youtube.com/watch?v=Ik_ODHmycMc&t=3s) | ABC News | 25-09-2026 |
| [6:17](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=377s) | [GV2F286IK1w @ 10:11](https://www.youtube.com/watch?v=GV2F286IK1w&t=611s) | Global Weather Network | 28-09-2026 |
| [6:25](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=385s) | [G9kimv0PiXU @ 2:48](https://www.youtube.com/watch?v=G9kimv0PiXU&t=168s) | CRISIS REPORT | 26-09-2026 |
| [6:34](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=394s) | [z40Etx7MqKA @ 14:03](https://www.youtube.com/watch?v=z40Etx7MqKA&t=843s) | Global Weather Network | 27-09-2026 |
| [6:53](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=413s) | [z40Etx7MqKA @ 1:48](https://www.youtube.com/watch?v=z40Etx7MqKA&t=108s) | Global Weather Network | 27-09-2026 |
| [7:05](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=425s) | [GV2F286IK1w @ 10:27](https://www.youtube.com/watch?v=GV2F286IK1w&t=627s) | Global Weather Network | 28-09-2026 |
| [8:07](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=487s) | [YINrD6007Tg @ 12:47](https://www.youtube.com/watch?v=YINrD6007Tg&t=767s) | Global Weather Network | 28-09-2026 |
| [8:21](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=501s) | [z40Etx7MqKA @ 13:53](https://www.youtube.com/watch?v=z40Etx7MqKA&t=833s) | Global Weather Network | 27-09-2026 |
| [8:30](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=510s) | [zO3JjQX1lGI @ 1:09](https://www.youtube.com/watch?v=zO3JjQX1lGI&t=69s) | Global Weather Network | 29-09-2026 |
| [8:56](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=536s) | [7sp6pQVVF_0 @ 0:11](https://www.youtube.com/watch?v=7sp6pQVVF_0&t=11s) | FOX Weather | 25-09-2026 |
| ″ | [J_YgKLOLxmo @ 1:17](https://www.youtube.com/watch?v=J_YgKLOLxmo&t=77s) | Global Weather Network | 29-09-2026 |
| [9:29](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=569s) | [i8LYD_HJVUc @ 3:05](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=185s) | Global Weather Network | 29-09-2026 |
| [9:39](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=579s) | [XQLImnJG4wQ @ 0:50](https://www.youtube.com/watch?v=XQLImnJG4wQ&t=50s) | Global Weather Network | 26-09-2026 |
| [9:46](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=586s) | [EF7GXcs8eXM @ 3:39](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=219s) | Global Weather Network | 30-09-2026 |
| [9:54](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=594s) | [GV2F286IK1w @ 5:25](https://www.youtube.com/watch?v=GV2F286IK1w&t=325s) | Global Weather Network | 28-09-2026 |
| [9:56](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=596s) | [EF7GXcs8eXM @ 3:16](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=196s) | Global Weather Network | 30-09-2026 |
| [10:00](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=600s) | [YINrD6007Tg @ 7:37](https://www.youtube.com/watch?v=YINrD6007Tg&t=457s) | Global Weather Network | 28-09-2026 |
| [10:05](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=605s) | [i8LYD_HJVUc @ 4:03](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=243s) | Global Weather Network | 29-09-2026 |
| [10:14](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=614s) | [J_YgKLOLxmo @ 1:37](https://www.youtube.com/watch?v=J_YgKLOLxmo&t=97s) | Global Weather Network | 29-09-2026 |
| [10:36](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=636s) | [XQLImnJG4wQ @ 2:27](https://www.youtube.com/watch?v=XQLImnJG4wQ&t=147s) | Global Weather Network | 26-09-2026 |
| [10:43](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=643s) | [i8LYD_HJVUc @ 29:53](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=1793s) | Global Weather Network | 29-09-2026 |
| [10:45](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=645s) | [i8LYD_HJVUc @ 29:55](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=1795s) | Global Weather Network | 29-09-2026 |
| [10:49](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=649s) | [7xW3Vbtf7Do @ 0:06](https://www.youtube.com/watch?v=7xW3Vbtf7Do&t=6s) | USA TODAY | 24-09-2026 |
| ″ | [YINrD6007Tg @ 8:33](https://www.youtube.com/watch?v=YINrD6007Tg&t=513s) | Global Weather Network | 28-09-2026 |
| [10:50](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=650s) | [7xW3Vbtf7Do @ 0:07](https://www.youtube.com/watch?v=7xW3Vbtf7Do&t=7s) | USA TODAY | 24-09-2026 |
| [10:52](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=652s) | [J_YgKLOLxmo @ 8:01](https://www.youtube.com/watch?v=J_YgKLOLxmo&t=481s) | Global Weather Network | 29-09-2026 |
| [10:58](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=658s) | [kuk4qcr8sPM @ 0:32](https://www.youtube.com/watch?v=kuk4qcr8sPM&t=32s) | ABC 7 Chicago | 24-09-2026 |
| [11:02](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=662s) | [z40Etx7MqKA @ 9:47](https://www.youtube.com/watch?v=z40Etx7MqKA&t=587s) | Global Weather Network | 27-09-2026 |
| [11:13](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=673s) | [EF7GXcs8eXM @ 2:22](https://www.youtube.com/watch?v=EF7GXcs8eXM&t=142s) | Global Weather Network | 30-09-2026 |
| ″ | [kuk4qcr8sPM @ 0:42](https://www.youtube.com/watch?v=kuk4qcr8sPM&t=42s) | ABC 7 Chicago | 24-09-2026 |
| [11:46](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=706s) | [GV2F286IK1w @ 3:49](https://www.youtube.com/watch?v=GV2F286IK1w&t=229s) | Global Weather Network | 28-09-2026 |
| [11:56](https://www.youtube.com/watch?v=wNCDK-l0oBw&t=716s) | [i8LYD_HJVUc @ 0:34](https://www.youtube.com/watch?v=i8LYD_HJVUc&t=34s) | Global Weather Network | 29-09-2026 |
