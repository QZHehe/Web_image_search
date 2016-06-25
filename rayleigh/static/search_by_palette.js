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
