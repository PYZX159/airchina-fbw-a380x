# A380X paintkit geometry and projection mapping

All work uses Blender CLI in background. Source OBJ is unmodified. Import settings: forward -Z, up Y. Blender version 5.2.3 LTS.

发布状态：**已由用户完成MSFS2024游戏内测试并确认发布**。本文记录离线几何流程；原始 paintkit、Blender 场景及几何缓存不随公开仓库分发。从最终九张 XCF 重导成品的流程见 [SOURCE-BUILD.md](../SOURCE-BUILD.md)，无需这些几何输入。

- Blender +X is aircraft port/left, confirmed by named PAX_DOOR_M1L geometry; -X is starboard/right.
- -Y is nose, +Y is tail; +Z is up. Units agree with metres (79.8677 m span, 73.0766 m overall length).
- Overall bounds: X -39.93384..39.93383; Y -35.19273..37.88386; Z -3.19018..20.15366.
- `geometry-report.json` has every mesh's coordinates bounds, material names, face counts, and UV layers, plus per-FUSE summaries.
- `A380X_FUSE{1..5}_coordinates_uv.npz` stores every polygon loop's world `xyz`, `uv`, face normal, and `face_offsets`. Faces are consecutive loop intervals `[face_offsets[i], face_offsets[i+1])`; therefore topology and seams can be reconstructed exactly.
- `A380X_FUSE{1..5}_uv.svg` shows all UV polygon boundaries, displayed with V upward. All five UV sets lie inside 0..1.

| Material | World Y | World Z | Coverage |
|---|---:|---:|---|
| FUSE1 | -35.1927..-14.8404 | -1.6614..6.7631 | Nose and forward fuselage, lower doors M1/M2, radome |
| FUSE2 | -15.4888..7.7473 | 0.7508..6.7657 | Centre fuselage |
| FUSE3 | 7.7473..30.0639 | -1.7207..6.7659 | Rear fuselage |
| FUSE4 | 18.5234..37.8839 | 1.9427..20.1537 | Fin/rudder, APU and horizontal stabilizers; includes X +/-15.15 m |
| FUSE5 | -19.3593..11.9180 | -2.4493..1.3536 | Belly and wing-box fairings |

`neutral-port-side.png` is viewed from +X, nose to image left. `neutral-starboard-side.png` is viewed from -X, nose to image right. `neutral-three-quarter.png` is a nose/starboard view. Cameras are included in `A380X-neutral-preview.blend`.

## Window/lettering placement

`window-boundaries.json` derives 222 window-hole boundary loops from the main fuselage topology. Main-deck windows centre around Z=2.140 m (edges approx 1.956..2.325). Upper-deck windows centre around Z=4.84 m (edges approx 4.686..4.990). Small curvature changes occur toward the ends.

Forward lower doors: M1 Y=-29.55..-28.16, M2 Y=-19.31..-17.99. Usable between-door lettering range is about Y=-27.7..-20.0. Lettering between decks fits Z=3.25..4.25 without crossing either window row. Lettering above the upper windows is limited by stronger fuselage curvature near Z=5.2..6.4.

## Agreed GIMP side projection

Opaque RGB source images: `artwork/projection/side_pos_x.png` and `side_neg_x.png`, each 8192x2560. World rectangle Y=-38..40 (78 m), Z=-4..20.375 (24.375 m), square world pixels at 105.02564 pixels/m.

- Port/+X: U=(Y+38)/78. Nose at image left.
- Starboard/-X: U=1-(Y+38)/78. Nose at image right. Text is independently laid out in normal reading order in this canvas.
- V=(Z+4)/24.375. In GIMP top-origin pixels: pixel_y=2560-(Z+4)*8192/78.
- Region outside this world rectangle returns white. X sign selects the side; face normals are not used.
- FUSE5 is filled uniform light grey, sRGB (0.92,0.93,0.94).

`bake_projection.py` was executed after root confirmed GIMP's PNGs were complete. It reconstructs one mesh per FUSE, uses Cycles CPU EMIT (no light/shadow baked), and outputs five 4096 RGBA PNGs with 16 px EXTEND margin at `artwork/baked/A380X_FUSE1.png` through `A380X_FUSE5.png`. Source alpha is intentionally ignored. UV-island pixels contain opaque RGB; unused texture space is transparent. Textured original-mesh previews and `A380X-projection-preview.blend` are in the same folder. Use CLI `-- --materials A380X_FUSE4` to re-bake just the tail after a projection revision; previews still load all five images.

The first Cycles bake produced opaque black outside UV coverage despite the initial transparent image color. This was corrected using a separate white EMIT UV mask with the same 16px margin; unused texels now have alpha 0 and island RGB is unchanged. The same mask correction is now built into `bake_projection.py`. Source and baked phoenix color were sampled directly from PNG bytes: most frequent flat red is exactly `#EB311D` in both, confirming no double sRGB/linear conversion.

## Final GIMP-composited previews

`render_final.py` reads the five `artwork/final/A380X_FUSE*_ALBEDO.PNG` images plus available engine and wingfence images. It applies them as sRGB images directly to Principled Base Color, uses Standard display with neutral illumination at one quarter of the initial studio energy, and packs all nine final PNGs (including the registration image) into `preview/airchina-a380x-preview.blend`. Its two side previews and 3/4 preview are `preview/airchina-port.png`, `airchina-starboard.png`, and `airchina-three-quarter.png`, each 2400x1200.

Final visual inspection confirms complete forward-facing phoenix marks on both sides, readable Chinese and English lettering, continuous main-deck window stripe across FUSE boundaries and door frames, and the fictional B-38AC registration. The registration image is packed for completeness; the paintkit OBJ has no separate registration material, while B-38AC is visible from the fuselage projection. These images are paintkit renders, not in-simulator captures. The user separately completed MSFS 2024 in-simulator testing and confirmed publication; this geometry record does not document individual LOD or door-animation test cases.

## DDS vertical orientation verified

GIMP helper opened the original FUSE1 DDS and exported PNG without flip. Applying that PNG directly to the OBJ UV aligns windshield mask, door frames and Spirit of Toulouse lettering. Explicit V flip badly misaligns them. See `dds-no-flip-on-obj.png` (correct) versus `dds-flip-y-on-obj.png` (incorrect). Preserve vertical orientation for Blender bake -> GIMP PNG -> DDS; no extra Y flip is needed.
