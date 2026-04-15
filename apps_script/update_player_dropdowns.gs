function updateDropdown() {
  // Get the form and the spreadsheet
  var form = FormApp.openById('1HGbpZ_jpBOSMqCiLlWPI8RaBeKdJtGFcvY-5RUF8jl8');
  var balanceForm = FormApp.openById('1gvLM-vfbb57cloiaXsQ_8u6-dBNj5yih5PHmfD5tmK0');
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

  // Update the dropdown options
  var formItems = form.getItems(FormApp.ItemType.LIST);
  var balanceFormItems = balanceForm.getItems(FormApp.ItemType.LIST);

  for (var i = 0; i < 4; i++) {
    formItems[i].asListItem().setChoiceValues(items);
    balanceFormItems[i].asListItem().setChoiceValues(items);
  }
}
