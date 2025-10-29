param(
	[string]$SectionId, # OneNote Section ID (e.g., 1401C2E5-CA97-41F7-BFC6-55C1BF00853D)
	[string]$Title = "Timesheet $(Get-Date -Format 'yyyy-MM-dd')",
	[string]$Content
)

$ErrorActionPreference = "Stop"
if (-not $SectionId) { throw "-SectionId is required" }
if (-not $Content) { $Content = "" }

# Create basic OneNote page XML per OneNote 2013 COM API
# We wrap content in a <one:Page> with an Outline containing HTML.
$escaped = [Security.SecurityElement]::Escape($Content)
$bodyHtml = "<html><body><pre style='font-family:Consolas,monospace;white-space:pre-wrap;'>$escaped</pre></body></html>"

$pageXml = @"
<?xml version="1.0"?>
<one:Page xmlns:one="http://schemas.microsoft.com/office/onenote/2013/onenote" name="$Title">
  <one:Outline>
    <one:OEChildren>
      <one:OE>
        <one:HTMLBlock>
          <one:Data><![CDATA[$bodyHtml]]></one:Data>
        </one:HTMLBlock>
      </one:OE>
    </one:OEChildren>
  </one:Outline>
</one:Page>
"@

$one = New-Object -ComObject OneNote.Application
[string]$newPageId = ""
$one.CreateNewPage($SectionId, [ref]$newPageId)
$one.UpdatePageContent($pageXml, $newPageId, 2) # 2 = force overwrite if needed

Write-Host "OneNote page created in section $SectionId with title '$Title' (PageId: $newPageId)."
