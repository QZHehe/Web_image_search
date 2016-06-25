/**
 * Created by qqq on 6/25/16.
 */
function getObjectKeys(object)
 {
     var keys = [];
     for (var property in object)
       keys.push(property);
     return keys;
 }

function getObjectValues(object)
 {
     var values = [];
     for (var property in object)
       values.push(object[property]);
     return values;
 }
function addShowSelectedColor(color)
{
    $colorName=color.id.replace('#','')
    $colorAdd = '<a id="show_'+$colorName+'"><span style="background-color: ';
    $colorAdd+= color.id+' " /></a> '
    $('#show_select_colors').append($colorAdd);
}
function deleteShowSelectedColor(color)
{
    $colorName=color.id.replace('#','')
    $colorDelete='show_'+$colorName;
    $('#'+$colorDelete).remove();
}