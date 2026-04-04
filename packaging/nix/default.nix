{ lib
, python3Packages
, fetchPypi
}:

python3Packages.buildPythonApplication rec {
  pname = "aceternity-mcp";
  version = "1.8.1";
  pyproject = true;

  src = fetchPypi {
    pname = "aceternity_mcp";
    inherit version;
    hash = "sha256-PLACEHOLDER";
  };

  build-system = with python3Packages; [
    hatchling
  ];

  dependencies = with python3Packages; [
    mcp
  ];

  pythonImportsCheck = [
    "aceternity_mcp"
  ];

  meta = with lib; {
    description = "MCP server for Aceternity UI components";
    homepage = "https://github.com/devinoldenburg/aceternity-mcp";
    license = licenses.mit;
    maintainers = [ ];
    mainProgram = "aceternity-mcp-server";
  };
}
