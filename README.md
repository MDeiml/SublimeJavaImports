SublimeJavaImports
==================

JavaImports is a Sublime Text 2 plugin for automatically adding imports to your Java files. It resolves the package names by scanning through a source .zip or folder or a .jar file.

Installation
------------

The best way to install this is using [PackageControl](https://sublime.wbond.net)

Usage
-----

First you have to define your `java_import_path` in your settings. The best path to use is the src.zip in your Java JDK.

To add an import either mark all class names to import and press `ctrl+alt+i` or just press `ctrl+alt+i` and then enter the class name.

To add a library to your project, in your `.sublime-project` add
<pre><code>"settings":
{
    "java_import_path":
    [
        "default/java/import/path/src.zip",
        "path/to/library.jar"
    ]
}
</code></pre>