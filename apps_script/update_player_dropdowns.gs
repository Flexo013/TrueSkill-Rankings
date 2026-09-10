// Per-game configuration.
var MATCH_FORM_ID = '1HGbpZ_jpBOSMqCiLlWPI8RaBeKdJtGFcvY-5RUF8jl8';
// Number of player dropdowns at the start of each form. Must match the
// max_players_per_match of the game's GameConfig.
var MAX_PLAYERS_PER_MATCH = 4;

function updateDropdown() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Players');

  // Get the data from the spreadsheet
  var lastRow = sheet.getLastRow();
  var data = sheet.getRange('B2:B').getValues();
  var items = data.map(function(row) {
    return String(row[0] || '').trim();
  }).filter(String);

  if (lastRow >= 2) {
    var latestPlayerCell = sheet.getRange(lastRow, 2);
    var latestPlayerName = String(latestPlayerCell.getValue() || '').trim();
    latestPlayerCell.setValue(latestPlayerName);
    items[items.length - 1] = latestPlayerName;

    if (latestPlayerName && items.slice(0, -1).indexOf(latestPlayerName) !== -1) {
      sheet.deleteRow(lastRow);
      items.pop();
    }
  }

  items.sort();

  // Update the dropdown options of the match form
  var form = FormApp.openById(MATCH_FORM_ID);
  var formItems = form.getItems(FormApp.ItemType.LIST);
  for (var i = 0; i < MAX_PLAYERS_PER_MATCH; i++) {
    formItems[i].asListItem().setChoiceValues(items);
  }
}
