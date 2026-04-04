class AceternityMcp < Formula
  include Language::Python::Virtualenv

  desc "MCP server for Aceternity UI components"
  homepage "https://github.com/devinoldenburg/aceternity-mcp"
  url "https://files.pythonhosted.org/packages/source/a/aceternity-mcp/aceternity_mcp-1.8.1.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "aceternity-mcp", shell_output("#{bin}/aceternity-mcp --version")
  end
end
