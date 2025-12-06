import json
import pathlib

with open("./asset/settings.json", "r", encoding="utf-8") as fp:
    settings = json.load(fp)

class Settings:
    class Editor:
        def file_encoding():        return settings["editor.file-encoding"]
        def lang():                 return settings["editor.lang"]
        def langfile():             return f"./asset/packages/lang/{settings["editor.lang"]}.json"
        def font():                 return settings["editor.font"]
        def font_size():            return settings["editor.fontsize"]
        def file_path():            return settings["editor.file-path"]
        def change(key, value):
            settings[f"editor.{key}"] = value

            with open("./asset/settings.json", "w", encoding="utf-8") as fp:
                json.dump(settings, fp)

    class Highlighter:
        def syntax_highlighting():  return settings["highlighter.syntax-highlighting"]

        def change(key, value):
            settings[f"highlighter.syntax-highlighting"][f"{key}"] = value

            with open("./asset/settings.json", "w", encoding="utf-8") as fp:
                json.dump(settings, fp)
    
    class Run:
        def timeout():
            if settings["race-mode"]: 
                return settings["run.timeout"] 
            else: 
                return None
    
    class Package:
        def themes():
            with open(f"{pathlib.Path.cwd().parent()}/asset/packages/packages/themes.json", "r", encoding="utf-8") as fp:
                return json.load(fp)
            
        def code_support():
            with open(f"{pathlib.Path.cwd().parent()}/asset/packages/packages/code_support.json", "r", encoding="utf-8") as fp:
                return json.load(fp)

    class Path:
        def main_dir():                  return pathlib.Path.cwd().parent()

    class AI:
        def get_api_key():          return settings["apikey"]
        
        def change(apikey):
            settings["apikey"] = apikey

            with open("./asset/settings.json", "w", encoding="utf-8") as fp:
                json.dump(settings, fp)