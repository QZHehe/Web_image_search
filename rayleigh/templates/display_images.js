var show_results = json_data['results'].slice((num-1)*20,num*20);
// var items = $.map(json_data['results'], function(val, i) {
var items = $.map(show_results, function(val, i) {
  var id = val['id'];
  var url = val['url'];
  var distance = sprintf('%.2f', val['distance']);
  var num = i;
  var a_search_by_image = sprintf('<a href="%s">检索此图</a>',
    sprintf('/search_by_image/%s/%s/%s/%s', sic_type, fea_type ,'no', id));
  var modify_image = sprintf('<a href="%s">颜色修正</a>',
    sprintf('/modify_image/%s/%s', sic_type, id));
  var a_id = sprintf('<a>%s</a>',id);
  var a_num = sprintf('<a>%s</a>',num.toString());
  // var img = sprintf('<img src="%s" alt="%.3f" width="%d" height="%d" class="img-thumbnail" />',
  //   '/static/'+url, val['distance'], val['width']/2, val['height']/2);
  var img = sprintf('<img src="%s" alt="%.3f" width="150px" class="img-thumbnail" />',
    '/static/'+url, val['distance']);
  var img_link = sprintf('<a href=%s>%s</a>', url, img);
  var caption = [a_search_by_image,modify_image].join(' | ');
  return sprintf('<div class="result">%s<br />%s</div>', img_link, caption)
});

var time = sprintf('索引时间: %.2f ms.<br />', json_data['time_elapsed']*1000);

$('#results').html(time+items.join(''));