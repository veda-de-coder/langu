import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter.font import Font
import io
import sys
from Lexer import Lexer
from parser import Parser
from interpreter import Interpreter

class OOPLanguageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OOP Language IDE")
        self.root.geometry("1000x700")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', padding=6)
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Red.TButton', foreground='white', background='#d9534f')
        self.style.configure('Green.TButton', foreground='white', background='#5cb85c')
        self.style.configure('Blue.TButton', foreground='white', background='#5bc0de')
        
        # Create widgets
        self.create_widgets()
        self.create_menu()
        self.create_toolbar()
        
        # Load example code
        self.load_example()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        self.root.config(menu=menubar)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, padding=(5, 2))
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        run_btn = ttk.Button(toolbar, text="Run", command=self.run_code, style='Green.TButton')
        run_btn.pack(side=tk.LEFT, padx=2)
        
        clear_btn = ttk.Button(toolbar, text="Clear", command=self.clear_code, style='Red.TButton')
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        save_btn = ttk.Button(toolbar, text="Save", command=self.save_file, style='Blue.TButton')
        save_btn.pack(side=tk.LEFT, padx=2)
        
        open_btn = ttk.Button(toolbar, text="Open", command=self.open_file, style='Blue.TButton')
        open_btn.pack(side=tk.LEFT, padx=2)
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Input panel
        input_frame = ttk.LabelFrame(main_frame, text="Source Code", padding=(5, 5))
        input_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Line numbers
        self.line_numbers = tk.Text(input_frame, width=4, padx=5, pady=5, 
                                   takefocus=0, border=0, background='#f0f0f0', 
                                   state='disabled', font=('Courier', 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Code editor with scrollbar
        self.code_input = tk.Text(input_frame, wrap=tk.NONE, undo=True, 
                                 font=('Courier', 10))
        self.code_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for syntax highlighting
        self.configure_tags()
        
        # Output panel
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding=(5, 5))
        output_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, state=tk.DISABLED, 
            font=('Courier', 10), background='#f8f8f8')
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.code_input.bind('<KeyRelease>', self.on_key_release)
        self.code_input.bind('<Configure>', self.update_line_numbers)
    
    def configure_tags(self):
        # Syntax highlighting tags
        self.code_input.tag_configure('keyword', foreground='blue')
        self.code_input.tag_configure('string', foreground='green')
        self.code_input.tag_configure('number', foreground='red')
        self.code_input.tag_configure('comment', foreground='gray')
    
    def update_line_numbers(self, event=None):
        lines = self.code_input.get('1.0', tk.END).count('\n') + 1
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
    
    def on_key_release(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()
    
    def highlight_syntax(self):
        # Basic syntax highlighting (expand this for full language support)
        text = self.code_input.get('1.0', tk.END)
        
        # Remove all tags
        for tag in self.code_input.tag_names():
            self.code_input.tag_remove(tag, '1.0', tk.END)
        
        # Apply keyword highlighting
        keywords = ['class', 'new', 'print']
        for word in keywords:
            start = '1.0'
            while True:
                start = self.code_input.search(word, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.code_input.tag_add('keyword', start, end)
                start = end
    
    def load_example(self):
        example_code = '''class Person {
    name = "John";
    age = 25;
}

person1 = new Person;
person1.name = "Alice";
person1.age = 30;

print person1.name;
print person1.age;

class Car {
    brand = "Toyota";
    model = "Camry";
}

car1 = new Car;
car1.brand = "Honda";
print car1.brand;
print car1.model;'''
        
        self.code_input.insert(tk.END, example_code)
        self.update_line_numbers()
        self.highlight_syntax()
    
    def run_code(self):
        code = self.code_input.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter some code to run.")
            return
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.status_bar.config(text="Running...")
        self.root.update()
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            lexer = Lexer(code)
            parser = Parser(lexer)
            ast = parser.parse()
            
            interpreter = Interpreter()
            interpreter.interpret(ast)
            
            output = captured_output.getvalue()
            if output:
                self.output_text.insert(tk.END, output)
            else:
                self.output_text.insert(tk.END, "Code executed successfully (no output)")
            
            self.status_bar.config(text="Execution completed")
                
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")
        
        finally:
            sys.stdout = old_stdout
            self.output_text.config(state=tk.DISABLED)
    
    def clear_code(self):
        self.code_input.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.update_line_numbers()
        self.status_bar.config(text="Ready")
    
    def new_file(self):
        self.clear_code()
        self.status_bar.config(text="New file created")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("OOP Files", "*.oop"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                self.clear_code()
                self.code_input.insert(tk.END, file.read())
            self.update_line_numbers()
            self.highlight_syntax()
            self.status_bar.config(text=f"Opened: {file_path}")
    
    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".oop",
            filetypes=[("OOP Files", "*.oop"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.code_input.get("1.0", tk.END))
            self.status_bar.config(text=f"Saved: {file_path}")
    
    def cut_text(self):
        self.code_input.event_generate("<<Cut>>")
    
    def copy_text(self):
        self.code_input.event_generate("<<Copy>>")
    
    def paste_text(self):
        self.code_input.event_generate("<<Paste>>")

def main():
    root = tk.Tk()
    app = OOPLanguageGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()