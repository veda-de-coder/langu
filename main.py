import tkinter as tk
from tkinter import scrolledtext, messagebox
import io
import sys
from Lexer import Lexer
from parser import Parser
from interpreter import Interpreter

class OOPLanguageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OOP Language Interpreter")
        self.root.geometry("800x600")
        
        self.create_widgets()
        
    def create_widgets(self):
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(input_frame, text="Code Input:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        self.code_input = scrolledtext.ScrolledText(input_frame, height=15, font=("Courier", 10))
        self.code_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        run_button = tk.Button(button_frame, text="Run Code", command=self.run_code, 
                              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        run_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear", command=self.clear_code,
                                bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        clear_button.pack(side=tk.LEFT, padx=5)
        
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(output_frame, text="Output:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10, font=("Courier", 10),
                                                    state=tk.DISABLED, bg="#f0f0f0")
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.load_example()
    
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
    
    def run_code(self):
        code = self.code_input.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "Please enter some code to run.")
            return
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
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
                
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}")
        
        finally:
            sys.stdout = old_stdout
        
        self.output_text.config(state=tk.DISABLED)
    
    def clear_code(self):
        self.code_input.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = OOPLanguageGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()