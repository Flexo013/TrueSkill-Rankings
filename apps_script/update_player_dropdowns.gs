function updateDropdown() {

  // Get the form and the spreadsheet
  var form = FormApp.openById('1HGbpZ_jpBOSMqCiLlWPI8RaBeKdJtGFcvY-5RUF8jl8'); // Submit Match
  var form2 = FormApp.openById('1gvLM-vfbb57cloiaXsQ_8u6-dBNj5yih5PHmfD5tmK0'); // Balance Teams

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Players');


  // Get the data from the spreadsheet
  var data = sheet.getRange('B2:B').getValues();

  var items = data.flat().filter(String);
  items.sort()


  // Get the dropdown questions in the forms
  var formItems = form.getItems(FormApp.ItemType.LIST);
  var formListItems = [];
  var form2Items = form2.getItems(FormApp.ItemType.LIST);
  var form2ListItems = [];

  // Update the dropdown options

  for (var counter = 0; counter < 4; counter = counter + 1) {
    formListItems.push(formItems[counter].asListItem());
    formListItems[counter].setChoiceValues(items);
    form2ListItems.push(form2Items[counter].asListItem());
    form2ListItems[counter].setChoiceValues(items);
  }

}
