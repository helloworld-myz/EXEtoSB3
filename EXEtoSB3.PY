# SPDX-License-Identifier: Apache-2.0
# ORIGINAL PROJECT: https://github.com/ZYF728/EXEtoSb3/ (first published on 2025-01-29)
# ORIGINAL COPYRIGHT: (c) 2025 ZYF728
#
# MODIFIED BY: SYSTEM_CPYTHON (BiliBili)
# MODIFICATION DATE: 2025-06-01
# MODIFICATION SUMMARY:
#   [EN] 1. Replaced Tkinter GUI with wxPython for better visual appearance
#        2. Added logging functionality to track conversion process
#        3. Improved error handling and user feedback
#        4. Added menu bar and about dialog
#        5. Enhanced file selection controls
#   [CN] 1. 使用wxPython替换Tkinter界面，提升视觉效果
#        2. 增加日志功能记录转换过程
#        3. 改进错误处理和用户反馈
#        4. 添加菜单栏和关于对话框
#        5. 增强文件选择控件

import os
import wx
import wx.adv
import threading
from os import makedirs, remove, rmdir, walk
from os.path import join, splitext, exists, basename
from zipfile import ZipFile

class EXEtoSB3Converter(wx.Frame):
    def __init__(self):
        super().__init__(None, title="EXE转SB3转换器", size=(750, 600))
        self.SetMinSize((750, 600))
        self.SetBackgroundColour(wx.Colour(240, 240, 245))
        
        self.input_file_path = ""
        self.output_dir_path = ""
        self.is_converting = False
        
        self.init_ui()
        self.create_menu()
        self.log("=== 程序初始化完成 ===")
        
    def init_ui(self):
        panel = wx.Panel(self)
        
        # 设置字体
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        
        # 标题
        title = wx.StaticText(panel, label="EXE转SB3转换器", pos=(30, 20))
        title.SetFont(title_font)
        
        # 输入文件部分
        wx.StaticText(panel, label="选择ZIP文件：", pos=(30, 70)).SetFont(label_font)
        self.input_text = wx.TextCtrl(panel, pos=(150, 65), size=(400, -1))
        browse_btn = wx.Button(panel, label="浏览", pos=(560, 65), size=(80, -1))
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse_file)
        
        # 输出目录部分
        wx.StaticText(panel, label="选择输出目录：", pos=(30, 120)).SetFont(label_font)
        self.output_text = wx.TextCtrl(panel, pos=(150, 115), size=(400, -1))
        dir_btn = wx.Button(panel, label="浏览", pos=(560, 115), size=(80, -1))
        dir_btn.Bind(wx.EVT_BUTTON, self.on_browse_dir)
        
        # 转换按钮
        self.convert_btn = wx.Button(panel, label="开始转换", pos=(300, 170), size=(150, 40))
        self.convert_btn.SetBackgroundColour(wx.Colour(76, 175, 80))
        self.convert_btn.SetForegroundColour(wx.WHITE)
        btn_font = self.convert_btn.GetFont()
        btn_font.SetPointSize(12)
        self.convert_btn.SetFont(btn_font)
        self.convert_btn.Bind(wx.EVT_BUTTON, self.on_convert)
        
        # 日志区域
        self.log_text = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL|wx.TE_RICH2,
            pos=(30, 230),
            size=(690, 300),
            value="操作日志：\n"
        )
        log_font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.log_text.SetFont(log_font)
        
        # 状态栏
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("准备就绪")
    
    def create_menu(self):
        menubar = wx.MenuBar()
        
        # 文件菜单
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, "打开文件(&O)")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "退出(&Q)")
        
        # 帮助菜单
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "关于(&A)")
        
        menubar.Append(file_menu, "文件(&F)")
        menubar.Append(help_menu, "帮助(&H)")
        
        self.SetMenuBar(menubar)
        
        # 绑定事件
        self.Bind(wx.EVT_MENU, self.on_menu_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_menu_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_menu_about, id=wx.ID_ABOUT)
    
    def on_browse_file(self, event):
        dialog = wx.FileDialog(
            self, 
            message="选择ZIP文件",
            wildcard="ZIP文件 (*.zip)|*.zip",
            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
        )
        if dialog.ShowModal() == wx.ID_OK:
            self.input_file_path = dialog.GetPath()
            self.input_text.SetValue(self.input_file_path)
            self.log(f"[文件] 已选择: {self.input_file_path}")
            self.update_status(f"已选择输入文件: {basename(self.input_file_path)}")
        dialog.Destroy()
        
    def on_browse_dir(self, event):
        dialog = wx.DirDialog(self, message="选择输出目录")
        if dialog.ShowModal() == wx.ID_OK:
            self.output_dir_path = dialog.GetPath()
            self.output_text.SetValue(self.output_dir_path)
            self.log(f"[目录] 已选择: {self.output_dir_path}")
            self.update_status(f"已选择输出目录: {basename(self.output_dir_path)}")
        dialog.Destroy()
        
    def on_convert(self, event):
        if self.is_converting:
            self.show_warning("当前已有转换任务正在进行")
            return
            
        if not self.validate_inputs():
            return
            
        self.is_converting = True
        self.convert_btn.Disable()
        self.log("\n=== 开始转换任务 ===")
        
        # 创建进度对话框
        self.progress_dialog = wx.ProgressDialog(
            "转换进度",
            "正在准备转换...",
            maximum=100,
            parent=self,
            style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT
        )
        
        # 在新线程中执行转换
        threading.Thread(target=self.run_conversion).start()
    
    def run_conversion(self):
        try:
            self.convert_exe_to_sb3(self.input_file_path, self.output_dir_path)
            wx.CallAfter(self.progress_dialog.Update, 100, "转换完成！")
            wx.CallAfter(self.show_info, "转换成功完成！", "完成")
        except Exception as e:
            wx.CallAfter(self.show_error, f"转换失败: {str(e)}", "错误")
            self.log(f"[错误] {str(e)}", error=True)
        finally:
            wx.CallAfter(self.progress_dialog.Destroy)
            wx.CallAfter(self.convert_btn.Enable)
            self.is_converting = False
    
    def convert_exe_to_sb3(self, zip_file_name, output_dir):
        wx.CallAfter(self.update_status, "正在验证输入文件...")
        if not os.path.exists(zip_file_name):
            raise ValueError("输入的ZIP文件不存在")
            
        file_name = basename(zip_file_name)
        target_zip_name = join(output_dir, splitext(file_name)[0] + ".sb3")
        
        # 准备临时目录
        temp_dir = join(output_dir, "temp_extract")
        wx.CallAfter(self.log, f"[系统] 创建临时目录: {temp_dir}")
        makedirs(temp_dir, exist_ok=True)
        
        # 解压文件 (步骤1/3)
        wx.CallAfter(self.progress_dialog.Update, 20, "正在解压文件...")
        wx.CallAfter(self.update_status, "正在解压文件...")
        self.log(f"[解压] 正在解压 {zip_file_name}")
        
        try:
            with ZipFile(zip_file_name, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except Exception as e:
            raise ValueError(f"解压失败: {str(e)}")
        
        # 查找资源目录 (步骤2/3)
        wx.CallAfter(self.progress_dialog.Update, 50, "正在查找资源...")
        app_dir = join(temp_dir, "resources", "app")
        if not exists(app_dir):
            raise ValueError(f"未找到资源目录: {app_dir}")
        
        # 创建SB3文件 (步骤3/3)
        wx.CallAfter(self.progress_dialog.Update, 70, "正在创建SB3文件...")
        self.log(f"[转换] 正在创建 {target_zip_name}")
        
        try:
            with ZipFile(target_zip_name, 'w') as new_zip:
                for root, dirs, files in walk(app_dir):
                    for file in files:
                        file_path = join(root, file)
                        arcname = join(self.custom_relpath(root, app_dir), file)
                        new_zip.write(file_path, arcname=arcname)
        except Exception as e:
            raise ValueError(f"创建SB3失败: {str(e)}")
        
        # 清理临时文件
        wx.CallAfter(self.progress_dialog.Update, 90, "正在清理...")
        self.cleanup_temp_dir(temp_dir)
        
        self.log(f"[完成] 输出文件: {target_zip_name}")
        wx.CallAfter(self.update_status, f"转换完成: {basename(target_zip_name)}")
    
    def cleanup_temp_dir(self, temp_dir):
        try:
            for root, dirs, files in walk(temp_dir, topdown=False):
                for name in files:
                    remove(join(root, name))
                for name in dirs:
                    rmdir(join(root, name))
            rmdir(temp_dir)
            self.log("[清理] 临时文件已删除")
        except Exception as e:
            self.log(f"[警告] 清理临时文件失败: {str(e)}", error=True)
    
    def validate_inputs(self):
        if not self.input_file_path:
            self.show_error("请先选择ZIP文件", "缺少输入文件")
            return False
            
        if not self.output_dir_path:
            self.show_error("请先选择输出目录", "缺少输出目录")
            return False
            
        if not os.path.exists(self.input_file_path):
            self.show_error("指定的ZIP文件不存在", "文件错误")
            return False
            
        return True
    
    # 以下是辅助方法
    def custom_relpath(self, path, start):
        path = os.path.abspath(os.path.normpath(path))
        start = os.path.abspath(os.path.normpath(start))
        if start not in path:
            return path
        common = os.path.commonprefix([path, start])
        rel_path = path[len(common):].lstrip(os.sep)
        parts = rel_path.split(os.sep)
        rel = []
        for part in parts:
            if part == '..':
                rel.pop()
            elif part != '.':
                rel.append(part)
        return os.sep.join(rel)
    
    def log(self, message, error=False):
        wx.CallAfter(self.log_text.AppendText, f"{message}\n")
        if error:
            wx.CallAfter(self.log_text.SetDefaultStyle, wx.TextAttr(wx.RED))
        wx.CallAfter(self.log_text.ShowPosition, self.log_text.GetLastPosition())
    
    def update_status(self, message):
        wx.CallAfter(self.status_bar.SetStatusText, message)
    
    def show_error(self, message, title="错误"):
        wx.CallAfter(wx.MessageBox, message, title, wx.OK|wx.ICON_ERROR)
    
    def show_warning(self, message, title="警告"):
        wx.CallAfter(wx.MessageBox, message, title, wx.OK|wx.ICON_WARNING)
    
    def show_info(self, message, title="提示"):
        wx.CallAfter(wx.MessageBox, message, title, wx.OK|wx.ICON_INFORMATION)
    
    # 菜单事件处理
    def on_menu_open(self, event):
        self.on_browse_file(event)
    
    def on_menu_exit(self, event):
        self.Close()
    
    def on_menu_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("EXE转SB3转换器")
        info.SetVersion("1.5")
        info.SetDescription("将EXE文件转换为Scratch 3.0项目文件\n\n")
        info.SetLicense("Apache 2.0 License")
        info.AddDeveloper("ZYF728(Github) 井TTA(哔哩哔哩)")
        info.AddDeveloper("SYSTEM_CPYTHON(哔哩哔哩)")
        info.SetWebSite("https://github.com/ZYF728/EXEtoSB3", "原项目主页")
        wx.adv.AboutBox(info)

def main():
    app = wx.App(False)
    frame = EXEtoSB3Converter()
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()