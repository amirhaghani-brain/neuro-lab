"""Tests for workspace discovery, classification, and templating."""

from pathlib import Path

from conftest import write
from neurolab.core.workspace import (
    TOOLS,
    classify_python_file,
    classify_python_source,
    create_file_from_template,
    find_all_workspace_files,
    list_root_scripts,
    list_tool_files,
    list_workspace_registry,
    scaffold_new_project,
)


class TestClassification:
    def test_brian2_source(self):
        assert classify_python_source("from brian2 import *\n") == {"brian2"}
        assert classify_python_source("import brian2 as b2\n") == {"brian2"}

    def test_neuron_source(self):
        assert classify_python_source("from neuron import h, gui\n") == {"neuron"}
        assert classify_python_source("import hoc\n") == {"neuron"}

    def test_nengo_source(self):
        assert classify_python_source("import nengo\n") == {"nengo"}

    def test_snntorch_source(self):
        assert classify_python_source("import snntorch as snn\n") == {"snntorch"}

    def test_neo_elephant_source(self):
        assert classify_python_source("import neo\nimport elephant\n") == {"neo"}

    def test_multi_framework_source(self):
        assert classify_python_source(
            "import brian2\nimport nengo\n"
        ) == {"brian2", "nengo"}

    def test_unclassified_source(self):
        assert classify_python_source("import numpy as np\n") == set()

    def test_file_read(self, workspace: Path):
        path = write(workspace / "models" / "sim.py", "from brian2 import *\n")
        assert classify_python_file(path) == {"brian2"}


class TestListToolFiles:
    def test_attributes_models_by_import(self, workspace: Path):
        write(workspace / "models" / "cortex.py", "from brian2 import *\n")
        write(workspace / "models" / "purkinje.py", "from neuron import h\n")
        write(workspace / "models" / "brain.py", "import nengo\n")

        brian2 = {p.name for p in list_tool_files("brian2", workspace)}
        neuron = {p.name for p in list_tool_files("neuron", workspace)}
        nengo = {p.name for p in list_tool_files("nengo", workspace)}

        assert brian2 == {"cortex.py"}
        assert neuron == {"purkinje.py"}
        assert nengo == {"brain.py"}

    def test_root_files_do_not_leak_into_toolchains(self, workspace: Path):
        write(workspace / "sim.py", "import math\n")
        for tool_id in TOOLS:
            names = {p.name for p in list_tool_files(tool_id, workspace)}
            assert "sim.py" not in names

    def test_unclassified_included_by_default(self, workspace: Path):
        write(workspace / "models" / "scratch.py", "import numpy as np\n")
        assert [p.name for p in list_tool_files("brian2", workspace)] == ["scratch.py"]
        assert list_tool_files("brian2", workspace, include_unclassified=False) == []

    def test_notebooks_match_by_extension(self, workspace: Path):
        write(workspace / "notebooks" / "exp.ipynb", "{}")
        assert [p.name for p in list_tool_files("jupyter", workspace)] == ["exp.ipynb"]

    def test_unknown_tool_returns_empty(self, workspace: Path):
        assert list_tool_files("does-not-exist", workspace) == []


class TestRootScripts:
    def test_lists_only_top_level_python(self, workspace: Path):
        write(workspace / "sim.py", "import math\n")
        write(workspace / "models" / "nested.py", "import math\n")
        write(workspace / "notes.txt", "hi\n")
        assert [p.name for p in list_root_scripts(workspace)] == ["sim.py"]


class TestRegistry:
    def test_no_file_appears_twice(self, workspace: Path):
        write(workspace / "models" / "cortex.py", "from brian2 import *\n")
        write(workspace / "models" / "purkinje.py", "from neuron import h\n")
        write(workspace / "models" / "scratch.py", "import numpy as np\n")
        write(workspace / "notebooks" / "exp.ipynb", "{}")
        write(workspace / "sim.py", "import math\n")

        registry = list_workspace_registry(workspace)
        all_paths = [p for files in registry.values() for p in files]
        assert len(all_paths) == len(set(all_paths))

        assert [p.name for p in registry["brian2"]] == ["cortex.py"]
        assert [p.name for p in registry["neuron"]] == ["purkinje.py"]
        assert [p.name for p in registry["unclassified"]] == ["scratch.py"]
        assert [p.name for p in registry["root"]] == ["sim.py"]
        assert [p.name for p in registry["jupyter"]] == ["exp.ipynb"]

    def test_empty_workspace(self, workspace: Path):
        assert list_workspace_registry(workspace) == {}


class TestTemplating:
    def test_create_file_uses_template(self, workspace: Path):
        created = create_file_from_template("brian2", "demo", workspace)
        assert created == workspace / "models" / "demo.py"
        assert "brian2" in created.read_text(encoding="utf-8")

    def test_create_file_avoids_overwrite(self, workspace: Path):
        first = create_file_from_template("brian2", "demo", workspace)
        second = create_file_from_template("brian2", "demo", workspace)
        assert first != second
        assert second.name == "demo_1.py"

    def test_scaffold_new_project(self, tmp_path: Path):
        project = scaffold_new_project(tmp_path / "fly", "fly")
        assert (project / "models").is_dir()
        assert (project / "notebooks").is_dir()
        assert (project / "README.md").read_text(encoding="utf-8").startswith("# fly")


class TestFindAll:
    def test_query_filters(self, workspace: Path):
        write(workspace / "models" / "cortex.py", "import math\n")
        write(workspace / "models" / "purkinje.py", "import math\n")
        hits = {p.name for p in find_all_workspace_files(workspace, "cortex")}
        assert hits == {"cortex.py"}

    def test_ignores_virtualenvs(self, workspace: Path):
        write(workspace / ".venv" / "lib" / "junk.py", "import math\n")
        write(workspace / "models" / "real.py", "import math\n")
        names = {p.name for p in find_all_workspace_files(workspace)}
        assert "junk.py" not in names
        assert "real.py" in names
