-- Convert PDF_FIELD_<asciiCamelCase> markers to named AcroForm fields.
local function field(inline)
  if inline.t ~= "Code" and inline.t ~= "Str" then return nil end
  local name, suffix = inline.text:match("^PDF_FIELD_([A-Za-z][A-Za-z0-9]*)(.*)$")
  if name then
    local control = pandoc.RawInline("latex", "\\TextField[name=" .. name .. ",width=48mm]{}\\relax{}")
    if suffix and suffix ~= "" then return {control, pandoc.Str(suffix)} end
    return control
  end
end

function Pandoc(doc)
  local blocks = pandoc.List({pandoc.RawBlock("latex", "\\begin{Form}")})
  for _, block in ipairs(doc.blocks) do
    blocks:insert(block:walk({Code = field, Str = field}))
  end
  blocks:insert(pandoc.RawBlock("latex", "\\end{Form}"))
  doc.blocks = blocks
  return doc
end
