# Validation recorded 2026-11-06

当前发布状态：**已由用户完成MSFS2024游戏内测试并确认发布**。本页同时记录静态文件检查与离线模型预览结果。

## Revision 0.1.1 after the first simulator test

The user's first simulator test found missing-texture pink checkerboards on all custom exterior sheets. The initial validator did not require MSFS `.DDS.json` bitmap descriptors; all nine had been omitted. The installed base aircraft and two working liveries contained descriptors for the corresponding DDS files.

Revision 0.1.1 adds nine Version 2 descriptors with compression/mipmap flags (and `HasTransp:true` for the cockpit registration), indexes all nine, and adds descriptor requirements to the package validation workflow. It preserves the DDS image bytes and compression. The updated check passed: **24 indexed content files, 159,450,700 content bytes**, with all nine descriptors present and indexed. These counts describe that historical check; the current package index is authoritative. The user subsequently completed MSFS 2024 in-simulator testing and confirmed publication.

## Initial revision 0.1.0 checks (historical; incomplete)

`Validate-Package.ps1` completed successfully after the nine DDS textures and two thumbnails were added and `Update-PackageLayout.ps1` rebuilt the package index.

- 15 indexed content files; 159,449,464 content bytes.
- Base A380X version inspected: `2024.1.0-161051add8a6959e3325289dbebe097c0793056f`.
- Base container, exterior/interior model XML references and texture fallback resolved against the installed aircraft.
- Seven 4096×4096 BC7 sRGB (DXGI 99) sheets, each with 13 mip levels.
- One 1024×1024 BC7 sRGB wingfence sheet, with 11 mip levels.
- One 1024×1024 DXT5/BC3 cockpit registration sheet, with 11 mip levels.
- No missing, duplicate or escaping layout paths; indexed sizes and manifest total matched.
- UV orientation checked using the original DDS and official OBJ; no vertical flip is applied.
- Both tail emblems and both sets of titles inspected in three-dimensional previews.
- Cockpit registration DDS reloaded in GIMP; transparent background and SELCAL retained.

The initial automated file-check workflow did not launch the simulator. The user subsequently completed MSFS 2024 in-simulator testing and confirmed publication. Preview images remain Blender renders of the final PNG source textures. The separate Native 2024 SDK draft was not compiled and is outside this Stable release.
