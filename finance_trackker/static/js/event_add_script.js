(function(){

 document.querySelector('#memberInput').addEventListener("keydoen', function(e){
    if (e.keycode != 13){
      return;
 }

  e.preventDefault()

  var categoryName=this.value
  this.value = ''
  addNewCategory(categoryName)
  updateCategoriesString()

})

function addNewCategory(name){

  document.querySelector('#categoriesContainer').insertAdjacentHTML('beforeend','
  <li clss="category">
        <span class="name">Development</span>
        <span onclick="removeCategory(this)" class="btnRemove bold">x</span>
      </li>')

}

function fetchCategoryArray(){
 var categories = []

 document.querySelectorAll('.category').forEach(function(e){
  name = e.querySelector'.name').innterHTML
   if (name == '') return;

  categories.push(name)

 })

 return categories

}

function updateCategoriesString(){
 categories = fetchCategoryArray()
 document.querySelector('input[name="categoriesString"]').value = categories.join(',')

}

function removeCategory(e){
 e.parentElement.remove()
 updateCategoriesString()

}


})()