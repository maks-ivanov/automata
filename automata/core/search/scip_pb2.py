# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: scip.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import enum_type_wrapper

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\nscip.proto\x12\x04scip"\x7f\n\x05Index\x12 \n\x08metadata\x18\x01 \x01(\x0b\x32\x0e.scip.Metadata\x12!\n\tdocuments\x18\x02 \x03(\x0b\x32\x0e.scip.Document\x12\x31\n\x10\x65xternal_symbols\x18\x03 \x03(\x0b\x32\x17.scip.SymbolInformation"\x9f\x01\n\x08Metadata\x12&\n\x07version\x18\x01 \x01(\x0e\x32\x15.scip.ProtocolVersion\x12!\n\ttool_info\x18\x02 \x01(\x0b\x32\x0e.scip.ToolInfo\x12\x14\n\x0cproject_root\x18\x03 \x01(\t\x12\x32\n\x16text_document_encoding\x18\x04 \x01(\x0e\x32\x12.scip.TextEncoding"<\n\x08ToolInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\x11\n\targuments\x18\x03 \x03(\t"\x84\x01\n\x08\x44ocument\x12\x10\n\x08language\x18\x04 \x01(\t\x12\x15\n\rrelative_path\x18\x01 \x01(\t\x12%\n\x0boccurrences\x18\x02 \x03(\x0b\x32\x10.scip.Occurrence\x12(\n\x07symbols\x18\x03 \x03(\x0b\x32\x17.scip.SymbolInformation"_\n\x06Symbol\x12\x0e\n\x06scheme\x18\x01 \x01(\t\x12\x1e\n\x07package\x18\x02 \x01(\x0b\x32\r.scip.Package\x12%\n\x0b\x64\x65scriptors\x18\x03 \x03(\x0b\x32\x10.scip.Descriptor"9\n\x07Package\x12\x0f\n\x07manager\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t"\x82\x02\n\nDescriptor\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rdisambiguator\x18\x02 \x01(\t\x12\'\n\x06suffix\x18\x03 \x01(\x0e\x32\x17.scip.Descriptor.Suffix"\xa5\x01\n\x06Suffix\x12\x15\n\x11UnspecifiedSuffix\x10\x00\x12\r\n\tNamespace\x10\x01\x12\x0f\n\x07Package\x10\x01\x1a\x02\x08\x01\x12\x08\n\x04Type\x10\x02\x12\x08\n\x04Term\x10\x03\x12\n\n\x06Method\x10\x04\x12\x11\n\rTypeParameter\x10\x05\x12\r\n\tParameter\x10\x06\x12\x08\n\x04Meta\x10\x07\x12\t\n\x05Local\x10\x08\x12\t\n\x05Macro\x10\t\x1a\x02\x10\x01"e\n\x11SymbolInformation\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x15\n\rdocumentation\x18\x03 \x03(\t\x12)\n\rrelationships\x18\x04 \x03(\x0b\x32\x12.scip.Relationship"\x82\x01\n\x0cRelationship\x12\x0e\n\x06symbol\x18\x01 \x01(\t\x12\x14\n\x0cis_reference\x18\x02 \x01(\x08\x12\x19\n\x11is_implementation\x18\x03 \x01(\x08\x12\x1a\n\x12is_type_definition\x18\x04 \x01(\x08\x12\x15\n\ris_definition\x18\x05 \x01(\x08"\xc8\x01\n\nOccurrence\x12\r\n\x05range\x18\x01 \x03(\x05\x12\x0e\n\x06symbol\x18\x02 \x01(\t\x12\x14\n\x0csymbol_roles\x18\x03 \x01(\x05\x12\x1e\n\x16override_documentation\x18\x04 \x03(\t\x12%\n\x0bsyntax_kind\x18\x05 \x01(\x0e\x32\x10.scip.SyntaxKind\x12%\n\x0b\x64iagnostics\x18\x06 \x03(\x0b\x32\x10.scip.Diagnostic\x12\x17\n\x0f\x65nclosing_range\x18\x07 \x03(\x05"\x80\x01\n\nDiagnostic\x12 \n\x08severity\x18\x01 \x01(\x0e\x32\x0e.scip.Severity\x12\x0c\n\x04\x63ode\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\x12\x0e\n\x06source\x18\x04 \x01(\t\x12!\n\x04tags\x18\x05 \x03(\x0e\x32\x13.scip.DiagnosticTag*1\n\x0fProtocolVersion\x12\x1e\n\x1aUnspecifiedProtocolVersion\x10\x00*@\n\x0cTextEncoding\x12\x1b\n\x17UnspecifiedTextEncoding\x10\x00\x12\x08\n\x04UTF8\x10\x01\x12\t\n\x05UTF16\x10\x02*}\n\nSymbolRole\x12\x19\n\x15UnspecifiedSymbolRole\x10\x00\x12\x0e\n\nDefinition\x10\x01\x12\n\n\x06Import\x10\x02\x12\x0f\n\x0bWriteAccess\x10\x04\x12\x0e\n\nReadAccess\x10\x08\x12\r\n\tGenerated\x10\x10\x12\x08\n\x04Test\x10 *\xea\x06\n\nSyntaxKind\x12\x19\n\x15UnspecifiedSyntaxKind\x10\x00\x12\x0b\n\x07\x43omment\x10\x01\x12\x18\n\x14PunctuationDelimiter\x10\x02\x12\x16\n\x12PunctuationBracket\x10\x03\x12\x0b\n\x07Keyword\x10\x04\x12\x19\n\x11IdentifierKeyword\x10\x04\x1a\x02\x08\x01\x12\x16\n\x12IdentifierOperator\x10\x05\x12\x0e\n\nIdentifier\x10\x06\x12\x15\n\x11IdentifierBuiltin\x10\x07\x12\x12\n\x0eIdentifierNull\x10\x08\x12\x16\n\x12IdentifierConstant\x10\t\x12\x1b\n\x17IdentifierMutableGlobal\x10\n\x12\x17\n\x13IdentifierParameter\x10\x0b\x12\x13\n\x0fIdentifierLocal\x10\x0c\x12\x16\n\x12IdentifierShadowed\x10\r\x12\x17\n\x13IdentifierNamespace\x10\x0e\x12\x18\n\x10IdentifierModule\x10\x0e\x1a\x02\x08\x01\x12\x16\n\x12IdentifierFunction\x10\x0f\x12 \n\x1cIdentifierFunctionDefinition\x10\x10\x12\x13\n\x0fIdentifierMacro\x10\x11\x12\x1d\n\x19IdentifierMacroDefinition\x10\x12\x12\x12\n\x0eIdentifierType\x10\x13\x12\x19\n\x15IdentifierBuiltinType\x10\x14\x12\x17\n\x13IdentifierAttribute\x10\x15\x12\x0f\n\x0bRegexEscape\x10\x16\x12\x11\n\rRegexRepeated\x10\x17\x12\x11\n\rRegexWildcard\x10\x18\x12\x12\n\x0eRegexDelimiter\x10\x19\x12\r\n\tRegexJoin\x10\x1a\x12\x11\n\rStringLiteral\x10\x1b\x12\x17\n\x13StringLiteralEscape\x10\x1c\x12\x18\n\x14StringLiteralSpecial\x10\x1d\x12\x14\n\x10StringLiteralKey\x10\x1e\x12\x14\n\x10\x43haracterLiteral\x10\x1f\x12\x12\n\x0eNumericLiteral\x10 \x12\x12\n\x0e\x42ooleanLiteral\x10!\x12\x07\n\x03Tag\x10"\x12\x10\n\x0cTagAttribute\x10#\x12\x10\n\x0cTagDelimiter\x10$\x1a\x02\x10\x01*V\n\x08Severity\x12\x17\n\x13UnspecifiedSeverity\x10\x00\x12\t\n\x05\x45rror\x10\x01\x12\x0b\n\x07Warning\x10\x02\x12\x0f\n\x0bInformation\x10\x03\x12\x08\n\x04Hint\x10\x04*N\n\rDiagnosticTag\x12\x1c\n\x18UnspecifiedDiagnosticTag\x10\x00\x12\x0f\n\x0bUnnecessary\x10\x01\x12\x0e\n\nDeprecated\x10\x02*\xe0\x08\n\x08Language\x12\x17\n\x13UnspecifiedLanguage\x10\x00\x12\x08\n\x04\x41\x42\x41P\x10<\x12\x07\n\x03\x41PL\x10\x31\x12\x07\n\x03\x41\x64\x61\x10\'\x12\x08\n\x04\x41gda\x10-\x12\x0c\n\x08\x41sciiDoc\x10V\x12\x0c\n\x08\x41ssembly\x10:\x12\x07\n\x03\x41wk\x10\x42\x12\x07\n\x03\x42\x61t\x10\x44\x12\n\n\x06\x42ibTeX\x10Q\x12\x05\n\x01\x43\x10"\x12\t\n\x05\x43OBOL\x10;\x12\x07\n\x03\x43PP\x10#\x12\x07\n\x03\x43SS\x10\x1a\x12\n\n\x06\x43Sharp\x10\x01\x12\x0b\n\x07\x43lojure\x10\x08\x12\x10\n\x0c\x43offeescript\x10\x15\x12\x0e\n\nCommonLisp\x10\t\x12\x07\n\x03\x43oq\x10/\x12\x08\n\x04\x44\x61rt\x10\x03\x12\n\n\x06\x44\x65lphi\x10\x39\x12\x08\n\x04\x44iff\x10X\x12\x0e\n\nDockerfile\x10P\x12\n\n\x06\x44yalog\x10\x32\x12\n\n\x06\x45lixir\x10\x11\x12\n\n\x06\x45rlang\x10\x12\x12\n\n\x06\x46Sharp\x10*\x12\x08\n\x04\x46ish\x10\x41\x12\x08\n\x04\x46low\x10\x18\x12\x0b\n\x07\x46ortran\x10\x38\x12\x0e\n\nGit_Commit\x10[\x12\x0e\n\nGit_Config\x10Y\x12\x0e\n\nGit_Rebase\x10\\\x12\x06\n\x02Go\x10!\x12\n\n\x06Groovy\x10\x07\x12\x08\n\x04HTML\x10\x1e\x12\x08\n\x04Hack\x10\x14\x12\x0e\n\nHandlebars\x10Z\x12\x0b\n\x07Haskell\x10,\x12\t\n\x05Idris\x10.\x12\x07\n\x03Ini\x10H\x12\x05\n\x01J\x10\x33\x12\x08\n\x04JSON\x10K\x12\x08\n\x04Java\x10\x06\x12\x0e\n\nJavaScript\x10\x16\x12\x13\n\x0fJavaScriptReact\x10]\x12\x0b\n\x07Jsonnet\x10L\x12\t\n\x05Julia\x10\x37\x12\n\n\x06Kotlin\x10\x04\x12\t\n\x05LaTeX\x10S\x12\x08\n\x04Lean\x10\x30\x12\x08\n\x04Less\x10\x1b\x12\x07\n\x03Lua\x10\x0c\x12\x0c\n\x08Makefile\x10O\x12\x0c\n\x08Markdown\x10T\x12\n\n\x06Matlab\x10\x34\x12\x07\n\x03Nix\x10M\x12\t\n\x05OCaml\x10)\x12\x0f\n\x0bObjective_C\x10$\x12\x11\n\rObjective_CPP\x10%\x12\x07\n\x03PHP\x10\x13\x12\t\n\x05PLSQL\x10\x46\x12\x08\n\x04Perl\x10\r\x12\x0e\n\nPowerShell\x10\x43\x12\n\n\x06Prolog\x10G\x12\n\n\x06Python\x10\x0f\x12\x05\n\x01R\x10\x36\x12\n\n\x06Racket\x10\x0b\x12\x08\n\x04Raku\x10\x0e\x12\t\n\x05Razor\x10>\x12\x08\n\x04ReST\x10U\x12\x08\n\x04Ruby\x10\x10\x12\x08\n\x04Rust\x10(\x12\x07\n\x03SAS\x10=\x12\x08\n\x04SCSS\x10\x1d\x12\x07\n\x03SML\x10+\x12\x07\n\x03SQL\x10\x45\x12\x08\n\x04Sass\x10\x1c\x12\t\n\x05Scala\x10\x05\x12\n\n\x06Scheme\x10\n\x12\x0f\n\x0bShellScript\x10@\x12\x0b\n\x07Skylark\x10N\x12\t\n\x05Swift\x10\x02\x12\x08\n\x04TOML\x10I\x12\x07\n\x03TeX\x10R\x12\x0e\n\nTypeScript\x10\x17\x12\x13\n\x0fTypeScriptReact\x10^\x12\x0f\n\x0bVisualBasic\x10?\x12\x07\n\x03Vue\x10\x19\x12\x0b\n\x07Wolfram\x10\x35\x12\x07\n\x03XML\x10\x1f\x12\x07\n\x03XSL\x10 \x12\x08\n\x04YAML\x10J\x12\x07\n\x03Zig\x10&B/Z-github.com/sourcegraph/scip/bindings/go/scip/b\x06proto3'
)

_PROTOCOLVERSION = DESCRIPTOR.enum_types_by_name["ProtocolVersion"]
ProtocolVersion = enum_type_wrapper.EnumTypeWrapper(_PROTOCOLVERSION)
_TEXTENCODING = DESCRIPTOR.enum_types_by_name["TextEncoding"]
TextEncoding = enum_type_wrapper.EnumTypeWrapper(_TEXTENCODING)
_SYMBOLROLE = DESCRIPTOR.enum_types_by_name["SymbolRole"]
SymbolRole = enum_type_wrapper.EnumTypeWrapper(_SYMBOLROLE)
_SYNTAXKIND = DESCRIPTOR.enum_types_by_name["SyntaxKind"]
SyntaxKind = enum_type_wrapper.EnumTypeWrapper(_SYNTAXKIND)
_SEVERITY = DESCRIPTOR.enum_types_by_name["Severity"]
Severity = enum_type_wrapper.EnumTypeWrapper(_SEVERITY)
_DIAGNOSTICTAG = DESCRIPTOR.enum_types_by_name["DiagnosticTag"]
DiagnosticTag = enum_type_wrapper.EnumTypeWrapper(_DIAGNOSTICTAG)
_LANGUAGE = DESCRIPTOR.enum_types_by_name["Language"]
Language = enum_type_wrapper.EnumTypeWrapper(_LANGUAGE)
UnspecifiedProtocolVersion = 0
UnspecifiedTextEncoding = 0
UTF8 = 1
UTF16 = 2
UnspecifiedSymbolRole = 0
Definition = 1
Import = 2
WriteAccess = 4
ReadAccess = 8
Generated = 16
Test = 32
UnspecifiedSyntaxKind = 0
Comment = 1
PunctuationDelimiter = 2
PunctuationBracket = 3
Keyword = 4
IdentifierKeyword = 4
IdentifierOperator = 5
Identifier = 6
IdentifierBuiltin = 7
IdentifierNull = 8
IdentifierConstant = 9
IdentifierMutableGlobal = 10
IdentifierParameter = 11
IdentifierLocal = 12
IdentifierShadowed = 13
IdentifierNamespace = 14
IdentifierModule = 14
IdentifierFunction = 15
IdentifierFunctionDefinition = 16
IdentifierMacro = 17
IdentifierMacroDefinition = 18
IdentifierType = 19
IdentifierBuiltinType = 20
IdentifierAttribute = 21
RegexEscape = 22
RegexRepeated = 23
RegexWildcard = 24
RegexDelimiter = 25
RegexJoin = 26
StringLiteral = 27
StringLiteralEscape = 28
StringLiteralSpecial = 29
StringLiteralKey = 30
CharacterLiteral = 31
NumericLiteral = 32
BooleanLiteral = 33
Tag = 34
TagAttribute = 35
TagDelimiter = 36
UnspecifiedSeverity = 0
Error = 1
Warning = 2
Information = 3
Hint = 4
UnspecifiedDiagnosticTag = 0
Unnecessary = 1
Deprecated = 2
UnspecifiedLanguage = 0
ABAP = 60
APL = 49
Ada = 39
Agda = 45
AsciiDoc = 86
Assembly = 58
Awk = 66
Bat = 68
BibTeX = 81
C = 34
COBOL = 59
CPP = 35
CSS = 26
CSharp = 1
Clojure = 8
Coffeescript = 21
CommonLisp = 9
Coq = 47
Dart = 3
Delphi = 57
Diff = 88
Dockerfile = 80
Dyalog = 50
Elixir = 17
Erlang = 18
FSharp = 42
Fish = 65
Flow = 24
Fortran = 56
Git_Commit = 91
Git_Config = 89
Git_Rebase = 92
Go = 33
Groovy = 7
HTML = 30
Hack = 20
Handlebars = 90
Haskell = 44
Idris = 46
Ini = 72
J = 51
JSON = 75
Java = 6
JavaScript = 22
JavaScriptReact = 93
Jsonnet = 76
Julia = 55
Kotlin = 4
LaTeX = 83
Lean = 48
Less = 27
Lua = 12
Makefile = 79
Markdown = 84
Matlab = 52
Nix = 77
OCaml = 41
Objective_C = 36
Objective_CPP = 37
PHP = 19
PLSQL = 70
Perl = 13
PowerShell = 67
Prolog = 71
Python = 15
R = 54
Racket = 11
Raku = 14
Razor = 62
ReST = 85
Ruby = 16
Rust = 40
SAS = 61
SCSS = 29
SML = 43
SQL = 69
Sass = 28
Scala = 5
Scheme = 10
ShellScript = 64
Skylark = 78
Swift = 2
TOML = 73
TeX = 82
TypeScript = 23
TypeScriptReact = 94
VisualBasic = 63
Vue = 25
Wolfram = 53
XML = 31
XSL = 32
YAML = 74
Zig = 38


_INDEX = DESCRIPTOR.message_types_by_name["Index"]
_METADATA = DESCRIPTOR.message_types_by_name["Metadata"]
_TOOLINFO = DESCRIPTOR.message_types_by_name["ToolInfo"]
_DOCUMENT = DESCRIPTOR.message_types_by_name["Document"]
_SYMBOL = DESCRIPTOR.message_types_by_name["Symbol"]
_PACKAGE = DESCRIPTOR.message_types_by_name["Package"]
_DESCRIPTOR = DESCRIPTOR.message_types_by_name["Descriptor"]
_SYMBOLINFORMATION = DESCRIPTOR.message_types_by_name["SymbolInformation"]
_RELATIONSHIP = DESCRIPTOR.message_types_by_name["Relationship"]
_OCCURRENCE = DESCRIPTOR.message_types_by_name["Occurrence"]
_DIAGNOSTIC = DESCRIPTOR.message_types_by_name["Diagnostic"]
_DESCRIPTOR_SUFFIX = _DESCRIPTOR.enum_types_by_name["Suffix"]
Index = _reflection.GeneratedProtocolMessageType(
    "Index",
    (_message.Message,),
    {
        "DESCRIPTOR": _INDEX,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Index)
    },
)
_sym_db.RegisterMessage(Index)

Metadata = _reflection.GeneratedProtocolMessageType(
    "Metadata",
    (_message.Message,),
    {
        "DESCRIPTOR": _METADATA,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Metadata)
    },
)
_sym_db.RegisterMessage(Metadata)

ToolInfo = _reflection.GeneratedProtocolMessageType(
    "ToolInfo",
    (_message.Message,),
    {
        "DESCRIPTOR": _TOOLINFO,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.ToolInfo)
    },
)
_sym_db.RegisterMessage(ToolInfo)

Document = _reflection.GeneratedProtocolMessageType(
    "Document",
    (_message.Message,),
    {
        "DESCRIPTOR": _DOCUMENT,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Document)
    },
)
_sym_db.RegisterMessage(Document)

Symbol = _reflection.GeneratedProtocolMessageType(
    "Symbol",
    (_message.Message,),
    {
        "DESCRIPTOR": _SYMBOL,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Symbol)
    },
)
_sym_db.RegisterMessage(Symbol)

Package = _reflection.GeneratedProtocolMessageType(
    "Package",
    (_message.Message,),
    {
        "DESCRIPTOR": _PACKAGE,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Package)
    },
)
_sym_db.RegisterMessage(Package)

Descriptor = _reflection.GeneratedProtocolMessageType(
    "Descriptor",
    (_message.Message,),
    {
        "DESCRIPTOR": _DESCRIPTOR,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Descriptor)
    },
)
_sym_db.RegisterMessage(Descriptor)

SymbolInformation = _reflection.GeneratedProtocolMessageType(
    "SymbolInformation",
    (_message.Message,),
    {
        "DESCRIPTOR": _SYMBOLINFORMATION,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.SymbolInformation)
    },
)
_sym_db.RegisterMessage(SymbolInformation)

Relationship = _reflection.GeneratedProtocolMessageType(
    "Relationship",
    (_message.Message,),
    {
        "DESCRIPTOR": _RELATIONSHIP,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Relationship)
    },
)
_sym_db.RegisterMessage(Relationship)

Occurrence = _reflection.GeneratedProtocolMessageType(
    "Occurrence",
    (_message.Message,),
    {
        "DESCRIPTOR": _OCCURRENCE,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Occurrence)
    },
)
_sym_db.RegisterMessage(Occurrence)

Diagnostic = _reflection.GeneratedProtocolMessageType(
    "Diagnostic",
    (_message.Message,),
    {
        "DESCRIPTOR": _DIAGNOSTIC,
        "__module__": "scip_pb2"
        # @@protoc_insertion_point(class_scope:scip.Diagnostic)
    },
)
_sym_db.RegisterMessage(Diagnostic)

if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z-github.com/sourcegraph/scip/bindings/go/scip/"
    _SYNTAXKIND._options = None
    _SYNTAXKIND._serialized_options = b"\020\001"
    _SYNTAXKIND.values_by_name["IdentifierKeyword"]._options = None
    _SYNTAXKIND.values_by_name["IdentifierKeyword"]._serialized_options = b"\010\001"
    _SYNTAXKIND.values_by_name["IdentifierModule"]._options = None
    _SYNTAXKIND.values_by_name["IdentifierModule"]._serialized_options = b"\010\001"
    _DESCRIPTOR_SUFFIX._options = None
    _DESCRIPTOR_SUFFIX._serialized_options = b"\020\001"
    _DESCRIPTOR_SUFFIX.values_by_name["Package"]._options = None
    _DESCRIPTOR_SUFFIX.values_by_name["Package"]._serialized_options = b"\010\001"
    _PROTOCOLVERSION._serialized_start = 1495
    _PROTOCOLVERSION._serialized_end = 1544
    _TEXTENCODING._serialized_start = 1546
    _TEXTENCODING._serialized_end = 1610
    _SYMBOLROLE._serialized_start = 1612
    _SYMBOLROLE._serialized_end = 1737
    _SYNTAXKIND._serialized_start = 1740
    _SYNTAXKIND._serialized_end = 2614
    _SEVERITY._serialized_start = 2616
    _SEVERITY._serialized_end = 2702
    _DIAGNOSTICTAG._serialized_start = 2704
    _DIAGNOSTICTAG._serialized_end = 2782
    _LANGUAGE._serialized_start = 2785
    _LANGUAGE._serialized_end = 3905
    _INDEX._serialized_start = 20
    _INDEX._serialized_end = 147
    _METADATA._serialized_start = 150
    _METADATA._serialized_end = 309
    _TOOLINFO._serialized_start = 311
    _TOOLINFO._serialized_end = 371
    _DOCUMENT._serialized_start = 374
    _DOCUMENT._serialized_end = 506
    _SYMBOL._serialized_start = 508
    _SYMBOL._serialized_end = 603
    _PACKAGE._serialized_start = 605
    _PACKAGE._serialized_end = 662
    _DESCRIPTOR._serialized_start = 665
    _DESCRIPTOR._serialized_end = 923
    _DESCRIPTOR_SUFFIX._serialized_start = 758
    _DESCRIPTOR_SUFFIX._serialized_end = 923
    _SYMBOLINFORMATION._serialized_start = 925
    _SYMBOLINFORMATION._serialized_end = 1026
    _RELATIONSHIP._serialized_start = 1029
    _RELATIONSHIP._serialized_end = 1159
    _OCCURRENCE._serialized_start = 1162
    _OCCURRENCE._serialized_end = 1362
    _DIAGNOSTIC._serialized_start = 1365
    _DIAGNOSTIC._serialized_end = 1493
# @@protoc_insertion_point(module_scope)
