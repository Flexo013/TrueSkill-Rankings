function updateDropdown() {
  // Get the form and the spreadsheet
  var form = FormApp.openById('1HGbpZ_jpBOSMqCiLlWPI8RaBeKdJtGFcvY-5RUF8jl8');
  var balanceForm = FormApp.openById('1gvLM-vfbb57cloiaXsQ_8u6-dBNj5yih5PHmfD5tmK0');
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Players');

  // Get the data from the spreadsheet: name (B), initialized (C), status (D)
  var lastRow = sheet.getLastRow();
  var data = sheet.getRange('B2:D').getValues();

  if (lastRow >= 2) {
    var latestPlayerCell = sheet.getRange(lastRow, 2);
    var latestPlayerName = String(latestPlayerCell.getValue() || '').trim();
    latestPlayerCell.setValue(latestPlayerName);

    var earlierNames = [];
    for (var r = 0; r + 2 < lastRow; r++) {
      earlierNames.push(String(data[r][0] || '').trim());
    }
    if (latestPlayerName && earlierNames.indexOf(latestPlayerName) !== -1) {
      sheet.deleteRow(lastRow);
      data.splice(lastRow - 2, 1);
    } else {
      data[lastRow - 2][0] = latestPlayerName;
    }
  }

  // Retired players stay on the sheet but are removed from the dropdowns.
  var items = [];
  data.forEach(function(row) {
    var name = String(row[0] || '').trim();
    var status = String(row[2] || '').trim();
    if (name && status !== 'RETIRED') {
      items.push(name);
    }
  });

  items.sort();

  // Update the dropdown options
  var formItems = form.getItems(FormApp.ItemType.LIST);
  var balanceFormItems = balanceForm.getItems(FormApp.ItemType.LIST);

  for (var i = 0; i < 4; i++) {
    formItems[i].asListItem().setChoiceValues(items);
    balanceFormItems[i].asListItem().setChoiceValues(items);
  }
}
