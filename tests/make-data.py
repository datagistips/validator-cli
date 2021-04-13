import pandas as pd

# Foo Data
data = pd.DataFrame(data = {
'id_site':[1,2,3], 
'foo1':['a', 'b', 'c'],
'foo2':['a', 'b', 'c'], 
'pattern':['b1', 'a2', 'a3'],
'list_values':['a', 'b', 'd'],
'date1':['2020-03-20', '2020-03-21', '2020-03-19'],
'date2':['2020-03-33', '2020-03-21', '2020-03-19'],
'date3':['21-01-2020', '21-01-2020', '21-01-2020'],
'ok1':[0, 1, 0],
'ok2':['TRUE', 'FALSE', 'TRUE'],
'ok3':['FALSE', False, True],
'ok4':[0, 1, 2],
'insee1' : ["5001", "75056", "751144"],
'siret1':["802954785000", "8029547850001899", "80295478500029"]

})

data.to_csv('data3.csv', index = False)

standard = pd.DataFrame(data = {
'name':['id_site', 'pattern', 'list_values', 'foo3', 'foo2', 'date1', 'date2', 'date3', 'ok1', 'ok2', 'ok3', 'ok4', 'insee1', 'siret1'], 
'type':['integer', 'character', 'character', 'character', 'integer', 'date', 'date', 'date', 'boolean','boolean','boolean','boolean', 'character', 'character'], 
'pattern':['', 'b[0-9]', '', '', '', '', '', '','','','','','^([013-9]\d|2[AB1-9])\d{3}$', '^\d{14}$'],
'enum':['','','["a", "b", "c"]', '', '', '', '', '','','','','','','']
})

standard.astype({'name': 'object', 'type':'object', 'pattern':'object', 'enum':'object'}).dtypes

standard.to_csv('standard3.csv', index = False)

