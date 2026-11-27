#nullable enable
using Godot;
using System;
using System.Linq;
using System.Text.Json;
namespace Ngumach.VisualReboot;

/// <summary>Shared indigo/violet translucent design system. No gameplay decisions.</summary>
public static class MoonGlassTheme
{
    private static readonly System.Collections.Generic.Dictionary<(Color,Color,int,int),StyleBoxFlat> Boxes=new();
    public static readonly Color Ink=Color.FromHtml("#f3f3ff"),Muted=Color.FromHtml("#bdc5e5"),Silver=Color.FromHtml("#aab6eb"),Gold=Color.FromHtml("#e5cda9");
    public static readonly Color Violet=Color.FromHtml("#b3a5ff"),Blue=Color.FromHtml("#80c9ff"),Hp=Color.FromHtml("#ff829a");
    public static readonly Color Glass=new(.16f,.17f,.29f,.80f),Surface=new(.25f,.26f,.42f,.65f);
    public static StyleBoxFlat Box(Color? fill=null,Color? border=null,int radius=10,int margin=12)
    {
        var key=(fill??Glass,border??new Color(.68f,.73f,.95f,.48f),radius,margin);
        if(Boxes.TryGetValue(key,out var cached))return cached;
        var box=new StyleBoxFlat{BgColor=key.Item1,BorderColor=key.Item2,
            BorderWidthLeft=1,BorderWidthRight=1,BorderWidthTop=1,BorderWidthBottom=1,
            CornerRadiusTopLeft=radius,CornerRadiusTopRight=radius,CornerRadiusBottomLeft=radius,CornerRadiusBottomRight=radius,
            ContentMarginLeft=margin,ContentMarginRight=margin,ContentMarginTop=margin,ContentMarginBottom=margin,
            ShadowColor=new Color(.015f,.02f,.08f,.32f),ShadowSize=6,ShadowOffset=new Vector2(0,3)};
        Boxes[key]=box;return box;
    }
    public static Theme Create()
    {
        var t=new Theme{DefaultFontSize=16};
        foreach(var type in new[]{"Label","Button","LineEdit","CheckButton","OptionButton"})t.SetColor("font_color",type,Ink);
        t.SetColor("default_color","RichTextLabel",Ink);
        t.SetColor("font_placeholder_color","LineEdit",new Color(.68f,.71f,.84f));
        t.SetColor("caret_color","LineEdit",Violet);
        t.SetStylebox("normal","LineEdit",Box(new Color(.09f,.10f,.21f,.62f),new Color(.5f,.55f,.78f,.4f),6,10));
        t.SetStylebox("focus","LineEdit",Box(new Color(.19f,.2f,.34f,.8f),Violet,6,10));
        foreach(var type in new[]{"VScrollBar","HScrollBar"})
        {
            t.SetStylebox("scroll",type,Box(new Color(.14f,.16f,.3f,.3f),Colors.Transparent,3,2));
            t.SetStylebox("grabber",type,Box(new Color(.62f,.64f,.85f,.65f),Colors.Transparent,3,3));
            t.SetStylebox("grabber_highlight",type,Box(Violet,Colors.Transparent,3,3));
        }
        return t;
    }
    public static Button Button(string text,float width=0,bool primary=false)
    {
        var b=new Button{Text=text,CustomMinimumSize=new Vector2(width,38),MouseDefaultCursorShape=Control.CursorShape.PointingHand};
        b.AddThemeFontSizeOverride("font_size",15);
        b.AddThemeColorOverride("font_color",Ink);b.AddThemeColorOverride("font_disabled_color",new Color(.58f,.62f,.76f));
        b.AddThemeStyleboxOverride("normal",Box(primary?new Color(.38f,.36f,.58f,.9f):Surface,primary?Gold:new Color(.6f,.65f,.9f,.4f),6,9));
        b.AddThemeStyleboxOverride("hover",Box(new Color(.39f,.4f,.64f,.94f),Silver,6,9));
        b.AddThemeStyleboxOverride("pressed",Box(new Color(.48f,.44f,.7f,.95f),Violet,6,9));
        b.AddThemeStyleboxOverride("disabled",Box(new Color(.15f,.17f,.28f,.5f),new Color(.4f,.44f,.6f,.25f),6,9));
        b.AddThemeStyleboxOverride("focus",Box(Colors.Transparent,Violet,6,9));
        return b;
    }
    public static Label Label(string text,int size=16,Color? color=null)
    {
        var l=new Label{Text=text,AutowrapMode=TextServer.AutowrapMode.WordSmart,SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};
        l.AddThemeFontSizeOverride("font_size",size);l.AddThemeColorOverride("font_color",color??Ink);return l;
    }
    public static PanelContainer Card(Color? fill=null)
    {var p=new PanelContainer{SizeFlagsHorizontal=Control.SizeFlags.ExpandFill};p.AddThemeStyleboxOverride("panel",Box(fill??Surface,new Color(.59f,.62f,.83f,.25f),8,12));return p;}
    public static Texture2D Portrait=>GD.Load<Texture2D>("res://assets/ui_moonglass/minh_kiem_portrait.png");
    public static Texture2D Hero(int direction=4)
    {
        using var d=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/reboot/manifest.json"));
        var frame=d.RootElement.GetProperty("heroFrames")[direction%8];var r=frame.GetProperty("rect");var b=frame.GetProperty("alphaBounds");
        return new AtlasTexture{Atlas=GD.Load<Texture2D>("res://assets/reboot/hero_idle_body.png"),Region=new Rect2(r[0].GetSingle()+b[0].GetSingle()-8,r[1].GetSingle()+b[1].GetSingle()-8,b[2].GetSingle()-b[0].GetSingle()+16,b[3].GetSingle()-b[1].GetSingle()+16),FilterClip=true};
    }
    public static TextureRect Image(Texture2D texture,Vector2 size,bool pixel=true)=>new(){Texture=texture,CustomMinimumSize=size,
        ExpandMode=TextureRect.ExpandModeEnum.IgnoreSize,StretchMode=TextureRect.StretchModeEnum.KeepAspectCentered,
        SizeFlagsHorizontal=Control.SizeFlags.ShrinkCenter,TextureFilter=pixel?CanvasItem.TextureFilterEnum.Nearest:CanvasItem.TextureFilterEnum.Linear,
        MouseFilter=Control.MouseFilterEnum.Ignore};
}
