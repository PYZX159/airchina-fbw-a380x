# A380X Air China Fictional packaging

The registration B-38AC and the Air China A380 represented by this repaint are fictional.

当前 Stable 涂装**已由用户完成MSFS2024游戏内测试并确认发布**。本文件另行说明包结构及历史 Native 草稿，不声称特定 LOD 或开门动画已逐项测试。

## Primary target: installed non-modular Stable aircraft

Base inspected on 2026-11-06:

- Base package folder: `flybywire-aircraft-a380-842`; supply its actual local path with `Validate-Package.ps1 -BasePackagePath`, or set `FBW_A380X_BASE_PATH`.
- Manifest title: `A380X (Stable)`
- Manifest version: `2024.1.0-161051add8a6959e3325289dbebe097c0793056f`
- VFS aircraft container: `SimObjects/AirPlanes/FlyByWire_A380_842`

The standalone repaint package is in `package/airchina-fbw-a380x-stable`.
It references the installed base aircraft and contains no aircraft models, systems or sounds. Its custom images include exterior albedo overrides and a cockpit-registration albedo override.
The variation preserves the base aircraft's manufacturer/type/creator grouping while the package manifest credits Eason.

Write finished DDS artwork to:

`package/airchina-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_AirChina_Fictional/texture.AIRCHINA/`

Legacy texture names:

| Native PNG source | Stable DDS output | Base dimensions |
| --- | --- | --- |
| A380X_FUSE1_ALBD.png | A380X_FUSE1_ALBEDO.PNG.DDS | 4096 x 4096 |
| A380X_FUSE2_ALBD.png | A380X_FUSE2_ALBEDO.PNG.DDS | 4096 x 4096 |
| A380X_FUSE3_ALBD.png | A380X_FUSE3_ALBEDO.PNG.DDS | 4096 x 4096 |
| A380X_FUSE4_ALBD.png | A380X_FUSE4_ALBEDO.PNG.DDS | 4096 x 4096 |
| A380X_FUSE5_ALBD.png | A380X_FUSE5_ALBEDO.PNG.DDS | 4096 x 4096 |
| A380X_EXT_ENG_LH_ALBD.png | A380_EXTERIOR_ENG_LH_ALBEDO.PNG.DDS | 4096 x 4096 |
| A380X_EXT_ENG_RH_ALBD.png | A380_EXTERIOR_ENG_RH_ALBEDO.PNG.DDS | 4096 x 4096 |
| A380X_REGISTRATION_ALBD.png | A380X_REGISTRATION_ALBEDO.PNG.DDS | 1024 x 1024 |
| A380X_EXT_WINGFENCE_ALBD.png | A380X_EXTERIOR_WINGFENCE_ALBEDO.PNG.DDS | 1024 x 1024 |

Only include textures actually painted. Missing textures fall back to the base aircraft.
The inspected base uses BC7 sRGB (DXGI 99) for fuselage, engine and wingfence albedo; its registration uses BC3/DXT5.
For an entirely GIMP workflow, BC3/DXT5 RGBA with a complete mipmap chain is a compatible export option.
Preserve the alpha channel, verify orientation against the paintkit, and do not include the paintkit's UV guides in exported artwork.
Do not convert material/normal maps unless they were intentionally changed.

After the artwork and thumbnail are final, regenerate `layout.json` and the manifest's `total_package_size`.
Generating an index performs static packaging work; the release's separate in-simulator test was completed by the user. Install the standalone livery into the active Community directory without replacing the base aircraft.

## Historical secondary draft: native modular MSFS 2024 aircraft

The local `project/A380X-AirChina-Fictional.xml` is an uncompiled source project based on the official Native 2024 Livery Creator Package v1.1; it is excluded from this public Stable release.
This source project is for the newer modular aircraft, not the installed Stable 2024.1.0 base.
Its PNG artwork and adjacent `.png.xml` texture settings live under:

`project/PackageSources/SimObjects/airplanes/FlyByWire_A380X/liveries/eason/AirChina_Fictional_B38AC/texture/`

Open the XML project in MSFS 2024 Developer Mode, verify Project Inspector metadata, replace template thumbnails, then use **Build & Export**.
The SDK compiles PNG textures into KTX2 with the template settings and mipmaps.
Distribute the compiled package only, not the source project.
This historical Native draft was not compiled or tested. The user's completed MSFS 2024 test and publication confirmation concern the non-modular Stable livery above.

## Provenance

- Official announcement: https://flybywiresim.com/notams/development-update-native-msfs-2024-a380x/
- Official template: https://flybywirecdn.com/addons/a380x/paintkit/A380X_Native_2024_Livery_Package_v1.1.zip
- Template SHA256: E78775F19B8D9ADDACAB548BEA299AB4A6B63E66FB6C034FC562820396126CBE
- The original template and its README/scripts are local external inputs, excluded from the public Stable source set; obtain the template from the official URL above for that optional workflow.
- The provided rename scripts were inspected as text and have not been executed.
- Microsoft model config reference: https://docs.flightsimulator.com/html/Content_Configuration/Models/model_cfg.htm
- Microsoft variation reference: https://docs.flightsimulator.com/html/Content_Configuration/SimObjects/Aircraft_SimO/aircraft_cfg.htm
