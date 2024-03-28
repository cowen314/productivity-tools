import tkinter as tk
from tkinter.constants import W
import time
from tkinter import filedialog
from version import version

class ToolUI():
    def __init__(self, namespace, template_url, dest_base_url, target_path, protocol, squash_commits):
        self.project_name = ""
        self.namespace = namespace
        self.template_url = template_url
        self.dest_base_url = dest_base_url
        self.target_path = target_path
        self.protocol = protocol
        self.squash_commits = squash_commits
    
    def setValues(self):
        if self.entry_project_name.get() != "":
            self.project_name = self.entry_project_name.get()
        if self.entry_namespace.get() != "":
            self.namespace = self.entry_namespace.get()
        if self.entry_template_url.get() != "":
            self.template_url = self.entry_template_url.get()
        if self.entry_dest_base_url.get() != "":
            self.dest_base_url = self.entry_dest_base_url.get()
        if self.entry_target_path.get() != "":
            self.target_path = self.entry_target_path.get()
        self.protocol = self.entry_protocol.get()
        self.squash_commits = self.entry_squash_commits.get() == 1
        #self.duplicate_text.set("Start Running...")
        self.root.destroy()

    def selectDirectory(self):
        targetPath = filedialog.askdirectory()
        self.entry_target_path.delete(0, tk.END)
        self.entry_target_path.insert(0, targetPath)

    def launchUI(self):
        #Main window
        self.root = tk.Tk()
        self.root.title(f"DMC Duplicate Repo Tool (v{version})")

        canvas = tk.Canvas(self.root, width=1350, height=300)
        canvas.grid(columnspan=5, rowspan=8)

        label_project_name = tk.Label(self.root, text="Enter the name of your repo / project (*MUST PROVIDE*):")
        label_project_name.grid(column=0, row=0, sticky=W)
        self.entry_project_name = tk.Entry(self.root, width=60)
        self.entry_project_name.grid(column=2, row=0, columnspan=2)

        label_namespace = tk.Label(self.root, text="Enter the project namespace (usually this has the format '<customerName>/', for example 'MyGreatCustomer/'; leave blank for default: 'DMC/labview/'):")
        label_namespace.grid(column=0, row=1, sticky=W)
        self.entry_namespace = tk.Entry(self.root, width=60)
        self.entry_namespace.grid(column=2, row=1, columnspan=2)

        label_template_url = tk.Label(self.root, text="Enter the template repository to copy to the newly created repo (leave blank for default: 'https://git.dmcinfo.com/DMC/labview/dmc-templates/labview-template-project.git'):")
        label_template_url.grid(column=0, row=2, sticky=W)
        self.entry_template_url = tk.Entry(self.root, width=60)
        self.entry_template_url.grid(column=2, row=2, columnspan=2)

        label_dest_base_url = tk.Label(self.root, text="Enter the URL base for the new Gitlab repo / project. This URL should not contain the namespace or project. (default: https://git.dmcinfo.com/):")
        label_dest_base_url.grid(column=0, row=3, sticky=W)
        self.entry_dest_base_url = tk.Entry(self.root, width=60)
        self.entry_dest_base_url.grid(column=2, row=3, columnspan=2)

        label_target_path = tk.Label(self.root, text="Enter the local path to copy files into (leave blank for this directory):")
        label_target_path.grid(column=0, row=4, sticky=W)
        self.entry_target_path = tk.Entry(self.root, width=60)
        self.entry_target_path.grid(column=2, row=4, columnspan=2)

        self.selectDirectory_text = tk.StringVar()
        selectDirectory_btn = tk.Button(self.root, textvariable = self.selectDirectory_text, command=self.selectDirectory, height=1, width=6)
        self.selectDirectory_text.set("Select")
        selectDirectory_btn.grid(column=1, row=4)

        label_protocol = tk.Label(self.root, text="Select protocol to use (HTTPS/SSH):")
        label_protocol.grid(column=0, row=5, sticky=W)
        self.entry_protocol = tk.StringVar(self.root, value="HTTPS")
        tk.Radiobutton(self.root, text="HTTPS", variable=self.entry_protocol, value="HTTPS").grid(column=2, row=5)
        tk.Radiobutton(self.root, text="SSH", variable=self.entry_protocol, value="SSH").grid(column=3, row=5)

        label_squash_commits = tk.Label(self.root, text="Squash commits in new repository?:")
        label_squash_commits.grid(column=0, row=6, sticky=W)
        self.entry_squash_commits = tk.IntVar(self.root, value=1)
        tk.Checkbutton(self.root, text="Squash?", variable=self.entry_squash_commits, onvalue=1, offvalue=0).grid(column=2, row=6, columnspan=2)
        
            
        self.duplicate_text = tk.StringVar()
        duplicate_btn = tk.Button(self.root, textvariable = self.duplicate_text, command=self.setValues, height=2, width=20)
        self.duplicate_text.set("Duplicate")
        duplicate_btn.grid(column=2, row=7, columnspan=2)

        #Run the main loop
        self.root.mainloop()

        # print("---Parameter Setting Completed---")
        # print("Project Name: %s" % toolUI.project_name)
        # print("Namespace: %s" % toolUI.namespace)
        # print("Template URL: %s" % toolUI.template_url)
        # print("Dest Base URL: %s" % toolUI.dest_base_url)
        # print("Target Path: %s" % toolUI.target_path)

if __name__ == "__main__":
    toolUI = ToolUI("DMC/labview/", "https://git.dmcinfo.com/DMC/labview/dmc-templates/labview-template-project.git", "https://git.dmcinfo.com/", ".", "HTTPS", 1)
    toolUI.launchUI()