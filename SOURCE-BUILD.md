# GIMP 源文件与重新导出

当前 Stable 涂装**已由用户完成MSFS2024游戏内测试并确认发布**。此文说明后续编辑与重新导出，不会将重新生成的文件视为已经完成新的游戏内测试。

## 恢复完整可编辑源文件

从同一版本 Release 下载 `AirChina-FBW-A380X-GIMP-Sources-v0.1.1.zip`，解压到仓库根目录，恢复以下 11 个文件：

- `artwork/xcf/` 中的九张最终 UV XCF：FUSE1—5、ENG_LH、ENG_RH、WINGFENCE，以及 `A380X_REGISTRATION_B38AC.xcf`。
- `artwork/projection/AirChina_side_pos_x.xcf` 与 `AirChina_side_neg_x.xcf`：左右机身投影母版。

原文件没有重新保存或压缩转换。逐文件原始大小及 SHA-256 见 [GIMP-SOURCES.json](GIMP-SOURCES.json)。本地制作目录另有 `artwork/source/A380X_REGISTRATION_B38AC.xcf`，其字节与 `artwork/xcf/` 中的同名文件完全相同，因此附件保留后者作为唯一规范路径；需要运行旧编号制作流程时可以自行复制该文件。

XCF 通过独立附件提供，是因为 FUSE4 的原始 XCF 为 141,243,505 字节，超过 GitHub 普通 Git 的单文件限制。其他必要图层没有被删减。

## 从九张最终 XCF 导出 Stable 成品

需要 PowerShell 7 与带 Python 批处理和 DDS 插件的 GIMP 3；本项目制作时使用 GIMP 3.2.8。修改并保存 XCF 后，在仓库根目录运行：

```powershell
.\Run-Gimp.ps1 -Script export_from_xcf_gimp.py

# GIMP 安装在其他位置时提供其实际路径：
.\Run-Gimp.ps1 -Script export_from_xcf_gimp.py -GimpExe 'D:\Apps\GIMP 3\bin\gimp-console-3.exe'

.\Update-PackageLayout.ps1
.\Validate-Package.ps1 -BasePackagePath 'D:\MSFS\Community\flybywire-aircraft-a380-842'
```

`Run-Gimp.ps1` 默认从当前 Windows 用户的 `LOCALAPPDATA\Programs\GIMP 3` 查找 GIMP，为批处理明确设置脚本的 `__file__` 和 `PROJECT_ROOT`，并使用项目内的独立 GIMP 配置目录。脚本和日志路径由项目根目录推导。校验器也可从环境变量 `FBW_A380X_BASE_PATH` 读取基础机模路径。

`export_from_xcf_gimp.py` 会在开始前检查九张 XCF 是否齐全；它读取图层可见性，导出 `artwork/final/*.PNG` 和 `package/airchina-fbw-a380x-stable/.../texture.AIRCHINA/*.DDS`，不会改写 XCF。八张外观贴图使用 BC7 sRGB 与完整 mipmap；驾驶舱编号使用保留透明的 BC3/DXT5。纹理保持原始 UV 方向，不额外翻转 Y。注册号 XCF 文件名中的 `B38AC` 映射到游戏要求的 `A380X_REGISTRATION_ALBEDO.PNG.DDS`。

此流程只需最终 XCF 与本仓库脚本，**不需要 FBW paintkit、Blender、模板 PNG 或几何缓存**。脚本只重新导出贴图；随后必须更新 `.DDS.json`、`layout.json` 和包大小，并校验重新生成的包。

## 可选：重新制作投影或几何预览

`create_projection_gimp.py` 使用 `resources/airchina/` 下的三个品牌 SVG 生成两侧构图；中文题字从原企业矢量裁出，机号文字使用本机 Arial 字体。两个投影 XCF 可以直接在 GIMP 编辑。

从侧面构图重新烘焙 UV，或运行 `compose_final_gimp.py` 从模板与烘焙层重新合成，需要自行通过官方渠道取得 A380X paintkit 0.3，准备 `resources/paintkit/A380X_PAINTKIT_V0.3.psd` 与 `A380X_PAINTKIT.obj`。这些上游原件不随本仓库分发。

高级流程为：导出模板 → 制作或导出两侧投影 → 用 `geometry/inspect_geometry.py` 建立本地几何及 UV 缓存 → `geometry/bake_projection.py` 烘焙 → `compose_final_gimp.py` 合成 → 可选 `geometry/render_final.py` 预览。几何脚本需要 Blender Python 与 NumPy；详细坐标约定见 [geometry/GEOMETRY.md](geometry/GEOMETRY.md)。几何、缓存、原机 DDS 检查图与历史 Native SDK 草稿均为额外本地输入，不属于九 XCF 直导流程。

`helper_registration_make.py` 是原始驾驶舱编号编辑流程，需要先准备原机注册号贴图的无翻转 PNG；日常修改无需再次运行它，直接编辑附件中的最终编号 XCF 即可。`Sync-NativeSources.ps1` 仅服务未编译的历史 Native 草稿，需要自行取得官方 Native 模板，不用于此 Stable 成品。
