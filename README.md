# EXEtoSB3
**将TurboWarp打包的EXE文件转换为Scratch 3.0项目（SB3格式）的工具**  


## 📌 核心功能
- **将TurboWarp打包的EXE文件转换为Scratch 3.0项目（SB3格式）**
- **操作要求**：  
  1. **仅压缩EXE文件本身**：需将目标EXE文件以及其他支持库文件、文件夹压缩为ZIP格式（**勿包含EXE文件所在文件夹**）。  
  2. **依赖环境**：使用源码运行时需提前安装 `wxPython`：
     ```bash  
     pip install wxPython
     
## ⚠️ 注意事项
- **文件格式限制：**
  必须为 TurboWarp 原生打包的 EXE，不支持加密或二次修改的文件。
- **路径要求：**
  文件路径中避免使用中文或特殊符号（如 ★、@ 等），可能导致解析失败。

## 📦 下载与安装
- **下载RELEASES里的源码或下载打包好的文件**

## 🤝 感谢与协议  
- **本项目基于 [原EXEtoSb3项目](https://github.com/ZYF728/EXEtoSb3) 开发，遵循 **Apache 2.0开源协议**（见 [LICENSE](LICENSE)）。**
- **允许商业使用、修改和分发，但需保留原作者和本项目的版权声明**
