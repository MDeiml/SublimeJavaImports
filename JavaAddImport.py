import os
import zipfile
import sublime
import sublime_plugin


def inside_module(filepath, modules):
        for m in modules:
                if filepath.startswith(m):
                        return m
        return None


def get_classes_list(path):
        if path.endswith(".zip") or path.endswith(".jar"):
                zipF = zipfile.ZipFile(path, "r")
                
                modules = []
                classesList = []
                for filename in zipF.namelist():
                    if filename.endswith("module-info.java"):
                        modules.append(os.path.dirname(filename))
                        continue

                    modulepath = inside_module(filename, modules)
                    classpath = ""
                    if modulepath:
                            classpath = filename[len(modulepath) + 1:] #module/

                    if classpath.endswith(".java"):
                            classpath = classpath[:-5]
                    elif classpath.endswith(".class"):
                                    classpath = classpath[:-6]
                    else:
                        continue

                    classpath = classpath.replace("/", ".")
                    classpath = classpath.replace("\\", ".")

                    classesList.append(classpath)
 
                
                zipF.close()
                return classesList
        else:
                # true if is inside a module
                # false if is inside a package only (no external module)
                classesList = []
                modules = []

                for root, dirs, files in os.walk(path):
                        for filename in files:
                                if (filename == "module-info.java"):
                                        modules.append(root)
                                        continue

                                modulepath = inside_module(os.path.join(root, filename), modules)
                                classpath = ""
                                if modulepath:
                                        classpath = os.path.join(root, filename)[len(modulepath) + 1:] #module/
                                else:
                                        classpath = os.path.join(root, filename)[len(path) + 1:] #path/

                                if classpath.endswith(".java"):
                                        classpath = classpath[:-5]
                                elif classpath.endswith(".class"):
                                        classpath = classpath[:-6]
                                else:
                                        # not a java class
                                        # does not needed
                                        continue

                                classpath = classpath.replace("/", ".")
                                classpath = classpath.replace("\\", ".")

                                classesList.append(classpath)

                return classesList


classesList = []


class UpdateClassesListCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global classesList
		classesList = []
			
		settings = self.view.settings()
		if not settings.has("java_import_path"):
			settings = sublime.load_settings("JavaImports.sublime-settings")
			if not settings.has("java_import_path"):
				sublime.error_message("You must first define \"java_import_path\" in your settings")
				return
		if len(settings.get("java_import_path")) == 0:
			sublime.error_message("You must first define \"java_import_path\" in your settings")
			return
		
		for path in settings.get("java_import_path"):
			classesList = classesList + get_classes_list(path)


class JavaAddImport(sublime_plugin.TextCommand):
	# not a singleton
	# so we should keep classesList outside

	def __init__(self, *args):
		self.results = None
		super().__init__(*args)


	def finishUp(self, index):
		if index == -1:
			return
		self.view.run_command("java_add_import_insert", {"classpath":self.results[index]})


	def onDone(self, className):
		self.results = [c for c in classesList if c.split(".")[-1].startswith(className)]

		if len(self.results) == 1:
			self.finishUp(0)
		elif len(self.results) > 1:
			self.view.window().show_quick_panel(self.results, self.finishUp)
		else:
			sublime.error_message("There is no such class in \"java_import_path\"." + \
				"Try using ctrl+alt+u to update classes list or add needed library path to settings of plugin")


	def run(self, edit):
		allEmpty = True
		for sel in self.view.sel():
			if sel.empty():
				continue
			self.onDone(self.view.substr(sel))
			allEmpty = False
		if allEmpty:
			self.view.window().show_input_panel("Class name: ", "", self.onDone, None, None)


class JavaAddImportInsertCommand(sublime_plugin.TextCommand):
		def run(self, edit, classpath):
			for i in range(0,10000):
				point = self.view.text_point(i,0)
				region = self.view.line(point)
				line = self.view.substr(region)
				if "import" in line or "class" in line:
					self.view.insert(edit,point,"import "+classpath+";\n")
					break