using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;

var root = new DirectoryInfo(AppContext.BaseDirectory);
while (root is not null && !Directory.Exists(Path.Combine(root.FullName, "Client", "Assets", "Scripts"))) root = root.Parent;
if (root is null) throw new InvalidOperationException("Run inside the repository.");
var files = Directory.GetFiles(Path.Combine(root.FullName, "Client", "Assets", "Scripts"), "*.cs", SearchOption.AllDirectories);
if (files.Length == 0) throw new InvalidOperationException("No Unity sources found.");
int errors = 0;
string[][] profiles = [[], ["UNITY_EDITOR"], ["UNITY_EDITOR", "UNITY_6000_0_OR_NEWER"]];
foreach (var symbols in profiles)
foreach (var file in files)
{
    var options = new CSharpParseOptions(LanguageVersion.CSharp9, preprocessorSymbols: symbols);
    var tree = CSharpSyntaxTree.ParseText(File.ReadAllText(file), options, file);
    foreach (var problem in tree.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error))
    { Console.Error.WriteLine(problem); errors++; }
}
Console.WriteLine($"Unity source syntax: {files.Length} files × {profiles.Length} symbol profiles; {errors} errors. No Unity type/import/device verification.");
return errors == 0 ? 0 : 1;
