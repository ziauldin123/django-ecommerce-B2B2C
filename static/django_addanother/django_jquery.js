if (typeof django == 'undefined') django = {};
if (typeof django.jQuery == 'undefined') django.jQuery = $;

/* this function is defined in admin/jsi18n, if this wasn't loaded, we define it */
if (typeof interpolate == 'undefined'){
  interpolate = function(fmt, obj, named) {
    if (named) {
      return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
    } else {
      return fmt.replace(/%s/g, function(match){return String(obj.shift())});
    }
  };
}
