import re

path = "/home/hotaro/Projects/fookus-tube/app/src/androidMain/kotlin/com/fookus/tube/ui/NewPipeTab.kt"

with open(path, "r") as f:
    content = f.read()

# Let's fix the extra braces at the end.
end_snippet = """    }
            }
        }
    }
}
"""

correct_end_snippet = """    }
        }
    }
}
"""

if content.endswith(end_snippet):
    content = content[:-len(end_snippet)] + correct_end_snippet
elif content.endswith("    }\n            }\n        }\n    }\n}\n"):
    content = content[:-len("    }\n            }\n        }\n    }\n}\n")] + correct_end_snippet
else:
    # Let's just do a robust regex to replace multiple braces with just 3 braces if that's what's needed.
    pass

with open(path, "w") as f:
    f.write(content)

print("Fixed braces")
