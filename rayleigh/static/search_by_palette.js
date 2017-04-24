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
function addShowSelectedColors(colors)
{
    for (var color in colors)
    {
        $colorName = color.replace('#', '')
        $colorAdd = '<div class="row" id="show_' + $colorName + '">';
        $colorAdd += '<div class="colorPercetage"></div></div>';
        $('#show_select_colors').append($colorAdd);
        var name = 'show_' + $colorName;
        $('#' + name).find('.colorPercetage').slider({
            orientation: "horizontal",
            range: "min",
            max: 255,
            value: (colors[color]*255),
        });
        $('#'+name).children().children(".ui-slider-range").css('background',color)

    }

}
function addShowSelectedColor(color)
{
    $colorName=color.id.replace('#','')
    $colorAdd = '<div class="row" id="show_'+$colorName+'">';
    // $colorAdd+= color.id+' " /></a>';
    $colorAdd+='<div class="colorPercetage"></div></div>';
    $('#show_select_colors').append($colorAdd);
    var name = 'show_'+$colorName;
    $('#'+name).find('.colorPercetage').slider({
          orientation: "horizontal",
          range: "min",
          max: 255,
          value: 127,
      });
    $('#'+name).children().children(".ui-slider-range").css('background',color.id)


}
function deleteShowSelectedColor(color)
{
    $colorName=color.id.replace('#','')
    $colorDelete='show_'+$colorName;
    $('#'+$colorDelete).remove();
} 
function getValues()
{
    var values = [];
    $('.colorPercetage').each(function(){
        values.push(parseFloat($(this).slider('value')));
    });
    return values;
}
