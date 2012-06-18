/* UI classes define the DOM elements that make up a node */
var CollectionUI = Ext.extend(Ext.tree.TreeNodeUI, {
    render : function(){
        var rendered = this.rendered;
        CollectionUI.superclass.render.call(this);
        if(!rendered) {
            $(this.wrap).attr('id', 'collection-composer-'+this.node.attributes.nodeid);
            this.node.attributes.el = Ext.DomHelper.insertBefore(this.indentNode, {tag:'div', cls:'actions-wrapper', children:[
                {tag:'ul', cls:'actions', nodeurl:this.node.attributes.nodeurl, nodeid:this.node.attributes.nodeid, version:this.node.attributes.version, children:[
                    {tag:'li', children:[{tag:'a', cls:'action_collection_subcollection', html:'Add subcollections'}]},
                    {tag:'li', children:[{tag:'a', cls:'action_collection_module', html:'Add modules'}]},
                    {tag:'li', children:[{tag:'a', cls:'action_col_title', html:'Edit title'}]}
                ]}
            ]}).firstChild;
        }
    }
});

var SubCollectionUI = Ext.extend(Ext.tree.TreeNodeUI, {
    render : function(){
        var rendered = this.rendered;
        SubCollectionUI.superclass.render.call(this);
        if(!rendered) {
            $(this.wrap).attr('id', 'collection-composer-'+this.node.attributes.nodeid);
            this.node.attributes.el = Ext.DomHelper.insertBefore(this.indentNode, {tag:'div', cls:'actions-wrapper', children:[
                {tag:'ul', cls:'actions', nodeid:this.node.attributes.nodeid, version:this.node.attributes.version, children:[
                    {tag:'li', children:[{tag:'a', cls:'action_collection_subcollection', html:'Add subcollections'}]},
                    {tag:'li', children:[{tag:'a', cls:'action_collection_module', html:'Add modules'}]},
                    {tag:'li', children:[{tag:'a', cls:'action_subcol_title', html:'Edit title'}]},
                    {tag:'li', children:[{tag:'a', cls:'action_mark_for_deletion', html:'Remove from collection'}]}
                ]}
            ]}).firstChild;
        }
    }
});

var ModuleUI = Ext.extend(Ext.tree.TreeNodeUI, {
    render : function(){
        var rendered = this.rendered;
        ModuleUI.superclass.render.call(this);
        if(!rendered) {
            $(this.wrap).attr('id', 'collection-composer-'+this.node.attributes.nodeid);
            this.node.attributes.el = Ext.DomHelper.insertBefore(this.indentNode, {tag:'div', cls:'actions-wrapper', children:[
                {tag:'ul', cls:'actions', nodeid:this.node.attributes.nodeid, version:this.node.attributes.version, children:[
                    {tag:'li', children:[{tag:'a', cls:'action_module_title', html:'Edit title/version'}]},
                    {tag:'li', children:[{tag:'a', cls:'action_featured_links', html:'Edit featured links'}]},
                    {tag:'li', children:[{tag:'a', cls:'action_mark_for_deletion', html:'Remove from collection'}]}
                ]}
            ]}).firstChild;
        }
    }
});

/* These classes model the various different node types */
var Collection = Ext.extend(Ext.tree.TreeNode, {
    constructor: function(config) {
        Ext.apply(config, {}, { uiProvider: CollectionUI, cls: 'node-collection', iconCls: 'node-collection-icon' });
        Collection.superclass.constructor.call(this, config);
        if(config.children) {
            Ext.each(config.children, function(x){ this. appendChild(x); }, this);
        }
    }
});

var SubCollection = Ext.extend(Ext.tree.TreeNode, {
    constructor: function(config) {
        Ext.apply(config, {}, { uiProvider: SubCollectionUI, cls: 'node-subcollection', iconCls: 'node-subcollection-icon' });
        SubCollection.superclass.constructor.call(this, config);
        if(config.children) {
            Ext.each(config.children, function(x){ this. appendChild(x); }, this);
        }
    }
});

var Module = Ext.extend(Ext.tree.TreeNode, {
    constructor: function(config) {
        Ext.apply(config, {}, { uiProvider: ModuleUI, cls: 'node-module', iconCls: 'node-module-icon', leaf: true });
        Module.superclass.constructor.call(this, config);
    }
});

/* Find a node in a tree by uid attribute */
function find_treenode(node, nodeid)
{
    if (node.attributes.nodeid == nodeid)
        return node;
    
    var children = node.childNodes;
    for(var i=0; i<children.length; i++)
    {
        var result = find_treenode(children[i], nodeid);
        if (result)
            return result;
    }

    return null;
};
