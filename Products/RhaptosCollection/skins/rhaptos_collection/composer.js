// Die Internet Explorer die
$.ajaxSetup({
    cache: false
});

Ext.BLANK_IMAGE_URL = '++resource++collection-composer-resources/transparent.gif';

// jQuery 1.1 has no hasClass method
function hasClass(obj, className) {
    if (typeof obj == 'undefined' || obj==null || !RegExp) { return false; }
    var re = new RegExp("(^|\\s)" + className + "(\\s|$)");
    if (typeof(obj)=="string") {
        return re.test(obj);
    }
    else if (typeof(obj)=="object" && obj.className) {
        return re.test(obj.className);
    }
    return false;
};

/* Popup window handles. Maybe put in a dictionary to fake a namespace? */
var window_remove_contained = false;    // to be refactored to be composer_window
var composer_window = false;

/* Global tree definition */
var collection_composer_tree = null;

var anchor_to_nodeurl = function(anchor) {
  var n = anchor.parent().parent().parent().parent().parent();
  var nodeurls = [];
  while(n.get().length > 0 && n.parent().get()[0] != collection_composer_tree.getRootNode().attributes.el.parentNode.parentNode.parentNode.parentNode) {
    var b = n.find('> div > div.actions-wrapper > ul.actions');
    if (b.attr('nodeid'))
      nodeurls.push(b.attr('nodeid'));
    n = n.parent();
  }

  nodeurls.push(collection_composer_tree.getRootNode().attributes.nodeurl);
  return nodeurls.reverse().join('/');
};

ComposerWindow = function(ev, config) {
  var config = config || {}; 
  var anchor = $(ev.getTarget());
  var nodeurl = anchor_to_nodeurl(anchor);
  var extra_qs = '';
  var params = '';
  if (config.extra_qs)
    extra_qs = config.extra_qs;
  // POST params
  if (config.params)
    params = config.params;

  // Calculate top of window
  // Place it on top of the browser window
  y = $(window).scrollTop() + 20; //add a little padding

  Ext.applyIf(config, {
    layout:'auto',
    modal: true,
    y: y,
    width:config.width,
    minHeight: 400,
    closeAction:'destroy',
    plain: true,
    title: config.title,
    autoScroll: true,
    shadow: false,
    autoLoad: {url: nodeurl + '/' + config.url + '?some_random_id='+Math.random() + extra_qs, scripts: true, params: params},
    listeners: {
        'beforedestroy': function(){
            if (hasClass(document.getElementById('collection-composer-popup'), 'modified'))
                return window.confirm('You have unsaved changes. Are you sure you want to close this form?');
         }
    }
  });
 
  ComposerWindow.superclass.constructor.call(this, config);
 
  this.window = this;
};
Ext.extend(ComposerWindow, Ext.Window);
Ext.reg('composer_window', ComposerWindow);

var dispatch = {
    action_mark_for_deletion: function(ev) {

        // Change node UI so it looks 'deleted'
        var anchor = $(ev.getTarget());
        anchor.removeClass('action_mark_for_deletion');
        anchor.addClass('action_unmark_for_deletion');
        var ul = anchor.parent().parent();
        ul.parent().parent().parent().addClass('delete_me');
        path = anchor_to_nodeurl(anchor);
        
        window_remove_contained = new Ext.Window({
            layout:'auto',
            modal: true,
            y: $(window).scrollTop() + 20,
            width:400,
            minHeight: 400,
            closeAction:'destroy',
            plain: true,
            shadow: false,
            title: 'Remove from collection',
            autoLoad: {url: path + '/@@collection-composer-remove-contained', scripts:true},
            autoScroll: true,
            listeners: {
                'destroy': function(){
                    anchor.removeClass('action_unmark_for_deletion');
                    anchor.addClass('action_mark_for_deletion');
                    var ul = anchor.parent().parent();
                    ul.parent().prev('span').css('text-decoration', 'none');
                    ul.parent().parent().removeClass('node_content_delete');
                    ul.parent().parent().addClass('node_content');
                    ul.parent().parent().parent().removeClass('delete_me');
                }
            }
        });
        window_remove_contained.show(this);
    },

    action_unmark_for_deletion: function(ev) {
        var anchor = $(ev.getTarget());
        anchor.removeClass('action_unmark_for_deletion');
        anchor.addClass('action_mark_for_deletion');
        var ul = anchor.parent().parent();
        // Un-strikethrough title
        // nextAll not available in jquery 1.1.1
        //$(ul.parentNode).nextAll('span,h4').css('text-decoration', 'none');
        ul.parent().prev('span').css('text-decoration', 'none');
        ul.parent().parent().removeClass('node_content_delete');
        ul.parent().parent().addClass('node_content');
        ul.parent().parent().parent().removeClass('delete_me');
    },

    action_collection_subcollection: function(ev) {
        composer_window = new ComposerWindow(ev, {
            width: 650,
            title: 'Add subcollections',
            url: '@@collection-composer-collection-subcollection'
        });
        composer_window.show(this);
    },
 
    action_collection_module: function(ev) {
        // Encode already selected module ids as part of url
        var recursor = function(node){
            var result = '';
            var children = node.childNodes;
            for(var i=0; i<children.length; i++)
            {
                var nodeid = children[i].attributes.nodeid;
                if (nodeid.indexOf('subcollection') != 0)
                {
                    result = result + '&skip:list=' 
                        + children[i].attributes.nodeid; 
                }
                result = result + recursor(children[i]);
            };
            return result;
        };
        var params = 'skip:list=x';
        params = params + recursor(collection_composer_tree.getRootNode());

        composer_window = new ComposerWindow(ev, {
            width: 650,
            typicalheight: 400,
            title: 'Add module',
            url: '@@collection-composer-collection-module',
            params: params
        });
        composer_window.show(this);
    },
 
    action_col_title: function(ev) {
        composer_window = new ComposerWindow(ev, {
            width: 650,
            title: 'Edit collection title',
            url: '@@collection-composer-collection-title'
        });
        composer_window.show(this);
    },
 
    action_subcol_title: function(ev) {
        composer_window = new ComposerWindow(ev, {
            width: 650,
            title: 'Edit subcollection title',
            url: '@@collection-composer-subcollection-title'
        });
        composer_window.show(this);
    },
 
    action_featured_links: function(ev) {
        composer_window = new ComposerWindow(ev, {
            width: 650,
            title: 'Edit featured links',
            url: '@@collection-composer-featured-links'
        });
        composer_window.show(this);
    },
 
    action_module_title: function(ev) {
        composer_window = new ComposerWindow(ev, {
            width: 650,
            title: 'Override module title and set module version',
            url: '@@collection-composer-module-title'
        });
        composer_window.show(this);
    }
           
};
 
 
Ext.onReady(function(){

    // Load the tree definition
    $.ajax({
        url:'@@js-tree-definition?some_random_id=' + Math.random(),
        async: false,
        success: function(data){
            collection_composer_tree = eval(data);
        }     
    });

    // Event dispatch function
    var dispatcher = function(n, e) {
        if(dispatch[e.getTarget().className]) {
            dispatch[e.getTarget().className](e); 
        };
    }
 
    // Bind click event to event dispatcher
    collection_composer_tree.on('click', dispatcher);

    // Drag drop handlers
    collection_composer_tree.on('startdrag', function(tree, node, e){
        // Remove highlight from row
        $('#collection-composer-'+node.attributes.nodeid + ' div').removeClass('x-tree-node-over');
    });
    collection_composer_tree.on('enddrag', function(tree, node, e){
        // Remove highlight from row
        $('#collection-composer-'+node.attributes.nodeid + ' div').removeClass('x-tree-node-over');
    });

    var objectPath = function(tree, node) {
        var root = tree.getRootNode().attributes.el;
        var path = [];
        while(node && node.parentNode != root) {
            path.push(node.attributes.nodeid);
            node = node.parentNode;
        }
        path.pop();
        return path.reverse().join("/");
    };

    collection_composer_tree.on('beforenodedrop', function(e){
        var tree = e.tree;
        var node = e.dropNode;
        var target = e.target;
        var url = tree.getRootNode().attributes.nodeurl;
        url = url + '/@@collection-composer-drag-drop?path=' + objectPath(tree, node);
        if('append' == e.point) {
            url = url + '&new_parent_path=' + objectPath(tree, target);
        } else if('above' == e.point) {
            url = url + '&new_parent_path=' + objectPath(tree, target.parentNode);
            url = url + '&next_path=' + objectPath(tree, target);
        } else if('below' == e.point) {
            url = url + '&new_parent_path=' + objectPath(tree, target.parentNode);
            url = url + '&previous_path=' + objectPath(tree, target);
        }
        $('div#kss-spinner-base').show();
        $.ajax({
            type: 'GET',
            url: url,
            /* IE7 causes two things:
             * - a HTTP status=1223 instead of 204 (which jQuery handles)
             * - an Error with message "Operation Aborted"
             * Microsoft says the fix is to upgrade to IE8 and appears to be because the post is done synchronously
             */
            async: Ext.isIE7,
            error: function() { alert("There was a problem reorganizing the collection. Please refresh the page and try again."); },  
            complete: function() { $('div#kss-spinner-base').hide(); }
        }); 
    });
    
    // Render expanded tree
    collection_composer_tree.render('coursetree');
    collection_composer_tree.getRootNode().expand();
    // Show the instructions
    $('#cc-instructions').show();
    // Hide the "Loading ..." message
    $('#coursetree-loading').hide();

    // Show actions if tree is empty
    var wrapper_visibility = function() {
        // Show actions if tree is empty
        if (collection_composer_tree.getRootNode().childNodes.length == 0)
        {
            $('ul.x-tree-root-ct:first div.x-tree-node-el:first div.actions-wrapper').css('visibility', 'visible');
        } else {
            $('ul.x-tree-root-ct:first div.x-tree-node-el:first div.actions-wrapper').css('visibility', '');
        }
    };
    wrapper_visibility();
    collection_composer_tree.on('append', wrapper_visibility);
    collection_composer_tree.on('insert', wrapper_visibility);
    collection_composer_tree.on('remove', wrapper_visibility);

});
 
