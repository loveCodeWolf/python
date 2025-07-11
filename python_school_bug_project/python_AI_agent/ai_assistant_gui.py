# 在类的开头添加导入
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog , font
import threading
import json
import os
from tongyi import tongyi_chat, messages
from get_taobao_context import main as get_taobao_main, load_taobao_config

class AIAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI智能助手")
        self.root.geometry("1000x750")
        
        # 默认配置
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.api_key = "sk-wrilwzaclgftxgshxeienqtsjjmuqegomwhqeiskkmevvcpb"
        self.system_prompt = "你是一个智能助手，能够理解用户的自然语言请求，并自动调用对应的工具函数。"
        
        # 字体配置
        self.font_family = "Microsoft YaHei"
        self.font_size = 11
        self.chat_font = None
        self.input_font = None
        self.init_fonts()
        
        # 加载淘宝配置
        self.load_taobao_config()
        
        # 初始化系统消息
        self.init_system_message()
        
        self.create_widgets()
        
    def init_fonts(self):
        """初始化字体"""
        try:
            self.chat_font = font.Font(family=self.font_family, size=self.font_size)
            self.input_font = font.Font(family=self.font_family, size=self.font_size)
            # 添加markdown样式字体
            self.bold_font = font.Font(family=self.font_family, size=self.font_size, weight="bold")
            self.italic_font = font.Font(family=self.font_family, size=self.font_size, slant="italic")
            self.code_font = font.Font(family="Consolas", size=self.font_size-1)
            self.header_font = font.Font(family=self.font_family, size=self.font_size+2, weight="bold")
        except:
            # 如果指定字体不可用，使用默认字体
            self.chat_font = font.Font(family="Arial", size=self.font_size)
            self.input_font = font.Font(family="Arial", size=self.font_size)
            self.bold_font = font.Font(family="Arial", size=self.font_size, weight="bold")
            self.italic_font = font.Font(family="Arial", size=self.font_size, slant="italic")
            self.code_font = font.Font(family="Courier", size=self.font_size-1)
            self.header_font = font.Font(family="Arial", size=self.font_size+2, weight="bold")

    def load_taobao_config(self):
        """加载淘宝配置"""
        try:
            # 使用绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'taobao_config.json')

            config = load_taobao_config()
            self.current_token = config.get('_m_h5_tk', '')
            self.current_cookie = config.get('Cookie', '')
        except Exception as e:
            print(f"加载淘宝配置失败：{str(e)}")
            # 使用默认值
            self.current_token = 'f7402439e4aabe99dd1565fbb1f02c07'
            self.current_cookie = "thw=cn; useNativeIM=false; wwUserTip=false; wk_cookie2=1a70de4bfc25ec437f4a1c4aa167078b; wk_unb=UUpgQEnfcDI%2FNDbybQ%3D%3D; aui=2216012822830; mt=ci=0_0; cna=fRr9Hkp8Qx8CAXSUuI1YliUD; sgcookie=E100hkNDGSGhs%2BD66vhGirx%2FpwHoe9OnyZ2%2F%2FnIOwaroVvYEUFRAw4bKBg81W0UHC9sjYT8dHS5oNx3V8AfX1W875K24%2B4p%2FTbmQmY5jiCwfdcM%3D; csg=960cab23; lgc=tb861723892; cancelledSubSites=%5B%22xianyu%22%5D; dnk=tb861723892; skt=a86e446dd19e9a62; tracknick=tb861723892; sn=; uc3=nk2=F5RNY%2BrYR%2FKoNnw%3D&vt3=F8dD2f5uhkxR8SJ6DW0%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&id2=UUpgQEnfcDI%2FNDbybQ%3D%3D; existShop=MTc0ODcwNzAwMA%3D%3D; uc4=id4=0%40U2gqz6bzdMmbaNBblO42%2BG2uVnsIX2i5&nk4=0%40FY4GtKHkMLjSSJ2QZII0HB3UBwTfzQ%3D%3D; _cc_=VT5L2FSpdA%3D%3D; xlly_s=1; mtop_partitioned_detect=1; _m_h5_tk=f7402439e4aabe99dd1565fbb1f02c07_1749092566931; _m_h5_tk_enc=460e1311541850951a7f15a388520009; cookie2=197db9ae68b7dc9201c7fe896bb9164c; t=0c5a9f42bb378523e1046397d7699aed; _tb_token_=5e71de31785be; sca=54f5e408; _samesite_flag_=true; 3PcFlag=1749085092336; bxuab=0; x5sectag=501687; x5sec=7b2274223a313734393038353735362c22733b32223a2261613962343465666539343538383534222c22617365727665723b33223a22307c434c6a6367384947454d7561354962382f2f2f2f2f774561447a49794d5459774d5449344d6a49344d7a41374d53494a5932467763485636656d786c4d4c375270717747227d; isg=BH9_CryTK_Yz0yHcLQEkxFcYDlMJZNMGP0bfvhFMhi51IJ6iGTQtVgtzYvDeS6t-; tfstk=gXmZKltSjhKZ3UVTSDZVTFjrZWrTPoRWgmNbnxD0C5Vi5Ssq0WkkB5TvWjuEiXU_sVNf0mPEsias0xI4nxcvBS99RAHTDoAWNo-SBAFYridIbSbhxveVIRYQSd7lFdRWN3tBS9q2_QGXmYOnY-F3I-4gopP33Rq0I-jDLW24eZfiijvUt-eNIi20Iwb3UWV0mocmKpybt-q0mAHT0u13hPvx4LlnvG5Qd7DgTijPeRzMivbfciiTQPlZeWz7PDya774LHWztjXMmfcUpJwZxd4lqobAC550zUXzS7QSZafemTlikHFULomo4p2dVu7umC4308dxiLlPZaDhhnNrZofn4WVWvevqi94F8SedLLci7u7UFtCDIL54rufOdm5grKXzSA6s7q4hE0zql4S1YKiGxDV5cuP2LL79eL774oAnOefaCkZUOdJPWIP7AkP2LL79eLZQYWBwUNd4N."
    def init_system_message(self):
        """初始化系统消息"""
        global messages
        messages.clear()
        messages.append({"role": "system", "content": self.system_prompt})
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🤖 AI智能助手", font=("Microsoft YaHei", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))
        
        # 配置按钮框架
        config_frame = ttk.Frame(main_frame)
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(2, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # 配置按钮
        ttk.Button(config_frame, text="⚙️ API配置", command=self.open_api_config).grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        ttk.Button(config_frame, text="📝 System配置", command=self.open_system_config).grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(config_frame, text="🛒 淘宝配置", command=self.open_taobao_config).grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(config_frame, text="🎨 字体设置", command=self.open_font_config).grid(row=0, column=3, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # 对话显示区域
        chat_frame = ttk.LabelFrame(main_frame, text="💬 对话记录", padding="10")
        chat_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            height=22, 
            state=tk.DISABLED,
            font=self.chat_font,
            bg="#f8f9fa",
            relief=tk.FLAT,
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置文本标签样式
        self.setup_text_tags()
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="✏️ 输入消息", padding="10")
        input_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_text = tk.Text(
            input_frame, 
            height=4, 
            wrap=tk.WORD,
            font=self.input_font,
            relief=tk.FLAT,
            borderwidth=1,
            padx=8,
            pady=8
        )
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.input_text.bind('<Control-Return>', self.send_message_event)
        
        # 发送按钮
        send_button = ttk.Button(input_frame, text="📤 发送\n(Ctrl+Enter)", command=self.send_message)
        send_button.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 操作按钮框架
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=4, column=0, columnspan=3, pady=(0, 15))
        
        ttk.Button(action_frame, text="🗑️ 清空对话", command=self.clear_chat).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="💾 保存对话", command=self.save_chat).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="📂 加载对话", command=self.load_chat).pack(side=tk.LEFT)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("✅ 就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, font=("Microsoft YaHei", 9))
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
    def save_chat(self):
        """保存对话"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                content = self.chat_display.get("1.0", tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", "对话已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def load_chat(self):
        """加载对话"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("1.0", tk.END)
                self.chat_display.insert("1.0", content)
                self.chat_display.config(state=tk.DISABLED)
                messagebox.showinfo("成功", "对话已加载")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败：{str(e)}")
    def open_font_config(self):
        """打开字体配置窗口"""
        config_window = tk.Toplevel(self.root)
        config_window.title("字体设置")
        config_window.geometry("500x500")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # 创建配置框架
        frame = ttk.Frame(config_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 字体族选择 - 获取系统所有字体
        ttk.Label(frame, text="字体族:").pack(anchor=tk.W, pady=(0, 5))
        font_family_var = tk.StringVar(value=self.font_family)
        
        # 获取系统所有可用字体
        try:
            import tkinter.font as tkFont
            system_fonts = sorted(tkFont.families())
            # 将常用字体放在前面
            common_fonts = ["Microsoft YaHei", "SimSun", "SimHei", "Arial", "Times New Roman", "Courier New", "Consolas"]
            # 过滤掉已经在常用字体中的字体，避免重复
            other_fonts = [f for f in system_fonts if f not in common_fonts]
            font_families = common_fonts + ["---分隔线---"] + other_fonts
        except:
            # 如果获取失败，使用默认字体列表
            font_families = ["Microsoft YaHei", "SimSun", "SimHei", "Arial", "Times New Roman", "Courier New", "Consolas"]
        
        font_family_combo = ttk.Combobox(frame, textvariable=font_family_var, values=font_families, state="readonly")
        font_family_combo.pack(fill=tk.X, pady=(0, 15))
        
        # 字体大小选择
        ttk.Label(frame, text="字体大小:").pack(anchor=tk.W, pady=(0, 5))
        font_size_var = tk.IntVar(value=self.font_size)
        font_size_frame = ttk.Frame(frame)
        font_size_frame.pack(fill=tk.X, pady=(0, 15))
        
        font_size_scale = tk.Scale(font_size_frame, from_=8, to=20, orient=tk.HORIZONTAL, variable=font_size_var)
        font_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        font_size_label = ttk.Label(font_size_frame, text=str(self.font_size))
        font_size_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        def update_size_label(val):
            font_size_label.config(text=val)
            
        font_size_scale.config(command=update_size_label)
        
       # 预览区域
        ttk.Label(frame, text="预览:").pack(anchor=tk.W, pady=(10, 5))
        preview_frame = ttk.LabelFrame(frame, text="字体预览", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 20))  # 保持不变
        
        # 创建带滚动条的文本框 - 修复高度问题
        preview_text = scrolledtext.ScrolledText(preview_frame, height=6, wrap=tk.WORD, width=50)
        preview_text.pack(fill=tk.X, expand=False)  # 添加expand=False确保不会扩展
        preview_text.insert("1.0", "这是字体预览文本\nThis is font preview text\n**粗体文本** *斜体文本* `代码文本`\n# 标题文本\n- 列表项目")
        
        def update_preview():
            """更新预览"""
            try:
                family = font_family_var.get()
                size = font_size_var.get()
                
                # 更新预览字体
                preview_font = font.Font(family=family, size=size)
                preview_text.config(font=preview_font)
                
            except Exception as e:
                print(f"预览更新失败: {e}")
        
        # 绑定更新事件
        font_family_combo.bind('<<ComboboxSelected>>', lambda e: update_preview())
        font_size_scale.config(command=lambda val: [update_size_label(val), update_preview()])
        
        # 初始预览
        update_preview()
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        def apply_font():
            """应用字体设置"""
            try:
                self.font_family = font_family_var.get()
                self.font_size = font_size_var.get()
                
                # 重新初始化字体
                self.init_fonts()
                
                # 更新现有控件字体
                self.chat_display.config(font=self.chat_font)
                self.input_text.config(font=self.input_font)
                
                # 重新设置文本标签
                self.setup_text_tags()
                
                messagebox.showinfo("成功", "字体设置已应用")
                config_window.destroy()
                
            except Exception as e:
                messagebox.showerror("错误", f"应用字体失败：{str(e)}")
        
        def reset_font():
            """重置为默认字体"""
            font_family_var.set("Microsoft YaHei")
            font_size_var.set(11)
            update_preview()
            update_size_label("11")
        
        ttk.Button(button_frame, text="应用", command=apply_font).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="重置为默认", command=reset_font).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=config_window.destroy).pack(side=tk.LEFT)
    def parse_markdown(self, text):
        """解析markdown格式文本"""
        # 存储解析后的文本段落和对应的样式
        segments = []
        
        # 按行分割文本
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip():
                segments.append(("\n", "normal"))
                continue
                
            # 处理标题
            if line.startswith('###'):
                segments.append((line[3:].strip() + "\n", "header3"))
            elif line.startswith('##'):
                segments.append((line[2:].strip() + "\n", "header2"))
            elif line.startswith('#'):
                segments.append((line[1:].strip() + "\n", "header1"))
            # 处理列表
            elif line.strip().startswith(('- ', '* ', '+ ')):
                segments.append(("  • " + line.strip()[2:] + "\n", "list"))
            # 处理代码块
            elif line.strip().startswith('```'):
                segments.append((line + "\n", "code_block"))
            else:
                # 处理行内格式
                self.parse_inline_markdown(line + "\n", segments)
                
        return segments
    
    def parse_inline_markdown(self, text, segments):
        """解析行内markdown格式"""
        i = 0
        current_text = ""
        
        while i < len(text):
            # 处理粗体 **text**
            if text[i:i+2] == '**':
                if current_text:
                    segments.append((current_text, "normal"))
                    current_text = ""
                
                # 查找结束的 **
                end_pos = text.find('**', i+2)
                if end_pos != -1:
                    bold_text = text[i+2:end_pos]
                    segments.append((bold_text, "bold"))
                    i = end_pos + 2
                else:
                    current_text += text[i]
                    i += 1
            # 处理斜体 *text*
            elif text[i] == '*' and (i == 0 or text[i-1] != '*') and (i+1 >= len(text) or text[i+1] != '*'):
                if current_text:
                    segments.append((current_text, "normal"))
                    current_text = ""
                
                # 查找结束的 *
                end_pos = text.find('*', i+1)
                if end_pos != -1:
                    italic_text = text[i+1:end_pos]
                    segments.append((italic_text, "italic"))
                    i = end_pos + 1
                else:
                    current_text += text[i]
                    i += 1
            # 处理行内代码 `code`
            elif text[i] == '`':
                if current_text:
                    segments.append((current_text, "normal"))
                    current_text = ""
                
                # 查找结束的 `
                end_pos = text.find('`', i+1)
                if end_pos != -1:
                    code_text = text[i+1:end_pos]
                    segments.append((code_text, "code"))
                    i = end_pos + 1
                else:
                    current_text += text[i]
                    i += 1
            else:
                current_text += text[i]
                i += 1
        
        if current_text:
            segments.append((current_text, "normal"))
    
    def setup_text_tags(self):
        """设置文本标签样式"""
        # 配置现有标签
        self.chat_display.tag_configure("user", foreground="#2E86AB", font=self.chat_font)
        self.chat_display.tag_configure("assistant", foreground="#A23B72", font=self.chat_font)
        self.chat_display.tag_configure("system", foreground="#F18F01", font=self.chat_font)
        self.chat_display.tag_configure("timestamp", foreground="#666666", font=self.chat_font)
        
        # 配置markdown标签
        self.chat_display.tag_configure("normal", font=self.chat_font)
        self.chat_display.tag_configure("bold", font=self.bold_font)
        self.chat_display.tag_configure("italic", font=self.italic_font)
        self.chat_display.tag_configure("code", font=self.code_font, background="#f0f0f0", foreground="#d63384")
        self.chat_display.tag_configure("code_block", font=self.code_font, background="#f8f9fa", foreground="#212529")
        self.chat_display.tag_configure("header1", font=self.header_font, foreground="#212529")
        self.chat_display.tag_configure("header2", font=self.header_font, foreground="#495057")
        self.chat_display.tag_configure("header3", font=self.header_font, foreground="#6c757d")
        self.chat_display.tag_configure("list", font=self.chat_font, foreground="#495057")
    
    def append_to_chat(self, text, sender):
        """添加文本到对话显示区域（支持markdown）"""
        import datetime
        
        self.chat_display.config(state=tk.NORMAL)
        
        # 添加时间戳
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # 根据发送者设置不同的样式和图标
        if sender == "user":
            self.chat_display.insert(tk.END, f"👤 用户 [{timestamp}]\n", "timestamp")
            # 用户消息不需要markdown解析，直接显示
            self.chat_display.insert(tk.END, f"{text.replace('用户: ', '')}", "user")
        elif sender == "assistant":
            self.chat_display.insert(tk.END, f"🤖 AI助手 [{timestamp}]\n", "timestamp")
            # AI助手消息进行markdown解析
            content = text.replace('AI助手: ', '')
            segments = self.parse_markdown(content)
            
            for segment_text, style in segments:
                if style == "normal":
                    self.chat_display.insert(tk.END, segment_text, "assistant")
                else:
                    # 组合样式：assistant + markdown样式
                    combined_tag = f"assistant_{style}"
                    if combined_tag not in self.chat_display.tag_names():
                        # 创建组合标签
                        if style == "bold":
                            self.chat_display.tag_configure(combined_tag, foreground="#A23B72", font=self.bold_font)
                        elif style == "italic":
                            self.chat_display.tag_configure(combined_tag, foreground="#A23B72", font=self.italic_font)
                        elif style == "code":
                            self.chat_display.tag_configure(combined_tag, foreground="#d63384", font=self.code_font, background="#f0f0f0")
                        elif style.startswith("header"):
                            self.chat_display.tag_configure(combined_tag, foreground="#A23B72", font=self.header_font)
                        elif style == "list":
                            self.chat_display.tag_configure(combined_tag, foreground="#A23B72", font=self.chat_font)
                        else:
                            self.chat_display.tag_configure(combined_tag, foreground="#A23B72", font=self.chat_font)
                    
                    self.chat_display.insert(tk.END, segment_text, combined_tag)
                    
        elif sender == "system":
            self.chat_display.insert(tk.END, f"⚙️ 系统 [{timestamp}]\n", "timestamp")
            self.chat_display.insert(tk.END, f"{text}", "system")
        else:
            self.chat_display.insert(tk.END, text)
        
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def send_message_event(self, event):
        """处理Ctrl+Enter事件"""
        self.send_message()
        return 'break'
        
    def send_message(self):
        """发送消息"""
        user_input = self.input_text.get("1.0", tk.END).strip()
        if not user_input:
            return
            
        # 清空输入框
        self.input_text.delete("1.0", tk.END)
        
        # 显示用户消息
        self.append_to_chat(f"用户: {user_input}\n", "user")
        
        # 设置状态
        self.status_var.set("AI正在思考...")
        
        # 在新线程中处理AI响应
        threading.Thread(target=self.get_ai_response, args=(user_input,), daemon=True).start()
        
    def get_ai_response(self, user_input):
        """获取AI响应"""
        try:
            response = tongyi_chat(user_input, self.api_url, self.api_key)
            
            # 在主线程中更新UI
            self.root.after(0, self.display_ai_response, response)
            
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            self.root.after(0, self.display_ai_response, error_msg)
            
    def display_ai_response(self, response):
        """显示AI响应"""
        self.append_to_chat(f"AI助手: {response}\n\n", "assistant")
        self.status_var.set("就绪")
        
    def clear_chat(self):
        """清空对话记录"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # 重新初始化系统消息
        self.init_system_message()
        
        self.append_to_chat("对话已清空，系统已重新初始化\n\n", "system")
        
    def open_api_config(self):
        """打开API配置窗口"""
        config_window = tk.Toplevel(self.root)
        config_window.title("API配置")
        config_window.geometry("500x300")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # 创建配置框架
        frame = ttk.Frame(config_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # API URL配置
        ttk.Label(frame, text="API URL:").pack(anchor=tk.W, pady=(0, 5))
        url_entry = tk.Entry(frame, width=60)
        url_entry.pack(fill=tk.X, pady=(0, 15))
        url_entry.insert(0, self.api_url)
        
        # API Key配置
        ttk.Label(frame, text="API Key:").pack(anchor=tk.W, pady=(0, 5))
        key_entry = tk.Entry(frame, width=60, show="*")
        key_entry.pack(fill=tk.X, pady=(0, 15))
        key_entry.insert(0, self.api_key)
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_config():
            self.api_url = url_entry.get().strip()
            self.api_key = key_entry.get().strip()
            messagebox.showinfo("成功", "API配置已保存")
            config_window.destroy()
            
        def reset_config():
            url_entry.delete(0, tk.END)
            key_entry.delete(0, tk.END)
            url_entry.insert(0, "https://api.siliconflow.cn/v1/chat/completions")
            key_entry.insert(0, "sk-wrilwzaclgftxgshxeienqtsjjmuqegomwhqeiskkmevvcpb")
            
        ttk.Button(button_frame, text="保存", command=save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="重置为默认", command=reset_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=config_window.destroy).pack(side=tk.LEFT)
        
    def open_system_config(self):
        """打开System Prompt配置窗口"""
        config_window = tk.Toplevel(self.root)
        config_window.title("System Prompt配置")
        config_window.geometry("600x400")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # 创建配置框架
        frame = ttk.Frame(config_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="System Prompt (系统提示词):").pack(anchor=tk.W, pady=(0, 10))
        
        # 文本编辑区域
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        system_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=15)
        system_text.pack(fill=tk.BOTH, expand=True)
        system_text.insert("1.0", self.system_prompt)
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        def save_system():
            self.system_prompt = system_text.get("1.0", tk.END).strip()
            self.init_system_message()  # 重新初始化系统消息
            messagebox.showinfo("成功", "System Prompt已保存并应用")
            config_window.destroy()
            
        def reset_system():
            default_prompt = "你是一个智能助手，能够理解用户的自然语言请求，并自动调用对应的工具函数。"
            system_text.delete("1.0", tk.END)
            system_text.insert("1.0", default_prompt)
            
        ttk.Button(button_frame, text="保存并应用", command=save_system).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="重置为默认", command=reset_system).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=config_window.destroy).pack(side=tk.LEFT)
        
    def open_taobao_config(self):
        """打开淘宝配置窗口"""
        # 重新加载配置以获取最新值
        self.load_taobao_config()
        
        config_window = tk.Toplevel(self.root)
        config_window.title("淘宝配置")
        config_window.geometry("800x700")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # 创建淘宝配置对话框
        TaobaoConfigDialog(config_window, self.current_token, self.current_cookie, self.on_taobao_config_saved)
        
    def on_taobao_config_saved(self):
        """淘宝配置保存后的回调"""
        # 重新加载配置
        self.load_taobao_config()
        messagebox.showinfo("成功", "淘宝配置已更新")

class TaobaoConfigDialog:
    def __init__(self, window, current_token, current_cookie, callback):
        self.window = window
        self.current_token = current_token
        self.current_cookie = current_cookie
        self.callback = callback
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="淘宝参数配置", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Token配置
        token_frame = ttk.LabelFrame(main_frame, text="_m_h5_tk Token", padding="10")
        token_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.token_entry = tk.Entry(token_frame, width=80)
        self.token_entry.pack(fill=tk.X, pady=(0, 5))
        self.token_entry.insert(0, self.current_token)
        
        ttk.Label(token_frame, text="说明: 从浏览器Cookie中提取的_m_h5_tk值", foreground="gray").pack(anchor=tk.W)
        
        # Cookie配置
        cookie_frame = ttk.LabelFrame(main_frame, text="Cookie字符串", padding="10")
        cookie_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Cookie文本区域
        cookie_text_frame = ttk.Frame(cookie_frame)
        cookie_text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        self.cookie_text = scrolledtext.ScrolledText(cookie_text_frame, wrap=tk.WORD, height=10)
        self.cookie_text.pack(fill=tk.BOTH, expand=True)
        self.cookie_text.insert("1.0", self.current_cookie)
        
        ttk.Label(cookie_frame, text="说明: 从浏览器开发者工具中复制完整的Cookie字符串", foreground="gray").pack(anchor=tk.W)
        
        # 测试区域
        test_frame = ttk.LabelFrame(main_frame, text="测试配置", padding="10")
        test_frame.pack(fill=tk.X, pady=(0, 15))
        
        test_input_frame = ttk.Frame(test_frame)
        test_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(test_input_frame, text="测试商品ID:").pack(side=tk.LEFT)
        self.test_id_entry = tk.Entry(test_input_frame, width=20)
        self.test_id_entry.pack(side=tk.LEFT, padx=(10, 10))
        self.test_id_entry.insert(0, "887862383399")
        
        ttk.Button(test_input_frame, text="测试连接", command=self.test_connection).pack(side=tk.LEFT)
        
        # 测试结果显示
        self.test_result = scrolledtext.ScrolledText(test_frame, wrap=tk.WORD, height=6, state=tk.DISABLED)
        self.test_result.pack(fill=tk.X, pady=(10, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="重置", command=self.reset_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="关闭", command=self.window.destroy).pack(side=tk.LEFT)
        
    def test_connection(self):
        """测试连接"""
        test_id = self.test_id_entry.get().strip()
        if not test_id:
            messagebox.showwarning("警告", "请输入测试商品ID")
            return
            
        # 显示测试中状态
        self.test_result.config(state=tk.NORMAL)
        self.test_result.delete("1.0", tk.END)
        self.test_result.insert("1.0", "正在测试连接...\n")
        self.test_result.config(state=tk.DISABLED)
        
        # 在新线程中测试
        threading.Thread(target=self.run_test, args=(test_id,), daemon=True).start()
        
    def run_test(self, test_id):
        """运行测试"""
        try:
            # 临时更新配置进行测试
            token = self.token_entry.get().strip()
            
            # 这里可以调用get_taobao_context的测试函数
            result = get_taobao_main(test_id)
            
            if result and len(result) > 10:
                test_msg = f"测试成功！\n获取到评价数据：\n{result[:200]}..."
            else:
                test_msg = "测试失败：未能获取到有效数据"
                
        except Exception as e:
            test_msg = f"测试失败：{str(e)}"
            
        # 在主线程中更新UI
        self.window.after(0, self.update_test_result, test_msg)
        
    def update_test_result(self, message):
        """更新测试结果"""
        self.test_result.config(state=tk.NORMAL)
        self.test_result.delete("1.0", tk.END)
        self.test_result.insert("1.0", message)
        self.test_result.config(state=tk.DISABLED)
        
    def save_config(self):
        """保存配置"""
        try:
            token = self.token_entry.get().strip()
            cookie = self.cookie_text.get("1.0", tk.END).strip()
            
            if not token:
                messagebox.showwarning("警告", "请输入_m_h5_tk Token")
                return
                
            # 保存配置到JSON文件
            config = {
                "_m_h5_tk": token,
                "Cookie": cookie
            }

            # 获取当前脚本所在目录的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'taobao_config.json')

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
                
            messagebox.showinfo("成功", "配置已保存到 taobao_config.json")
            
            # 调用回调函数
            if self.callback:
                self.callback()
                
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{str(e)}")
            
    def reset_config(self):
        """重置配置"""
        self.token_entry.delete(0, tk.END)
        self.token_entry.insert(0, self.current_token)
        
        self.cookie_text.delete("1.0", tk.END)
        self.cookie_text.insert("1.0", self.current_cookie)
        
        self.test_result.config(state=tk.NORMAL)
        self.test_result.delete("1.0", tk.END)
        self.test_result.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = AIAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()