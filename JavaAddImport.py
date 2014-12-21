import sublime, sublime_plugin
import zipfile
import os

def get_classes_list(path):
	if path.endswith(".zip") or path.endswith(".jar"):
		print(path)
		return zipfile.ZipFile(path, "r").namelist()
	else:
		classesList = []
		for root, dirs, files in os.walk(path):
			for filename in files:
				classesList.append((root+"/"+filename)[len(path):])
		return classesList

class JavaAddImportCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		settings = self.view.settings()
		if not settings.has("java_import_path"):
			sublime.error_message("You must first define \"java_import_path\" in your settings")
			return
		if len(settings.get("java_import_path")) == 0:
			sublime.error_message("You must first define \"java_import_path\" in your settings")
			return
		classesList = []
		for path in settings.get("java_import_path"):
			classesList = classesList + get_classes_list(path)

		def onDone(className):
			results = []
			for name in classesList:
				if name.endswith("/"+className+".java") or name.endswith("\\"+className+".java") or name.endswith("/"+className+".class") or name.endswith("\\"+className+".class"):
					result = name.replace("/",".").replace("\\",".").replace(".java","").replace(".class", "")
					if result.startswith("."):
						result = result[1:]
					print(result)
					results.append(result)

			def finishUp(index):
				if index == -1:
					return
				for i in range(0,10000):
					point = self.view.text_point(i,0)
					region = self.view.line(point)
					line = self.view.substr(region)
					if "import" in line or "class" in line:
						self.view.insert(edit,point,"import "+results[index]+";\n")
						break
			if len(results) == 1:
				finishUp(0)
			elif len(results) > 1:
				self.view.window().show_quick_panel(results, finishUp)
			else:
				sublime.error_message("There is no such class in \"java_import_path\"")

		allEmpty = True
		for sel in self.view.sel():
			if sel.empty():
				continue
			onDone(self.view.substr(sel))
			allEmpty = False
		if allEmpty:
			self.view.window().show_input_panel("Class name: ", "", onDone, None, None)
