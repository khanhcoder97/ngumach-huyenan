#nullable enable
using Godot;
using System.Collections.Generic;
namespace Ngumach.VisualReboot;
public static class MoonGlassIcons
{
    private static readonly Dictionary<string,Texture2D> Cache=new();
    public static Texture2D Get(string key)
    {
        if(Cache.TryGetValue(key,out var t))return t;
        string path=key switch{
            "Character"=>"<circle cx='16' cy='10' r='5'/><path d='M6 28v-4c0-9 20-9 20 0v4M12 16l4 4 4-4'/>",
            "Inventory"=>"<path d='M7 11h18l3 17H4zM11 11V7c0-5 10-5 10 0v4M10 17h12M12 21h8'/>",
            "Skills"=>"<path d='M5 27L24 5l3 3L8 29M7 18l8 8M21 4l6 5M4 30l5-4'/>",
            "Journal"=>"<path d='M7 4h19v24H7c-6 0-6-6 0-6h19M7 4v18M12 10h9M12 15h7'/>",
            "WorldMap"=>"<path d='M3 7l8-3 10 4 8-3v21l-8 3-10-4-8 3zM11 4v21M21 8v21'/><circle cx='17' cy='15' r='2'/>",
            "Forge"=>"<path d='M8 3l13 6-4 7-13-6zM13 14L5 28l4 2 9-15M21 21h9M20 25h10M23 21v8'/>",
            "Guild"=>"<path d='M16 2l12 5v11c0 6-12 12-12 12S4 24 4 18V7zM16 8l2 6 6 1-5 4 1 6-4-3-5 3 1-6-5-4 6-1z'/>",
            "Activities"=>"<path d='M5 7h22v22H5zM10 2v9M22 2v9M5 14h22M11 19h3M19 19h3M11 24h3'/>",
            "Codex"=>"<path d='M16 7C11 2 3 3 3 3v23s8-1 13 3c5-4 13-3 13-3V3s-8-1-13 4v22M7 9l5 1M7 15l5 1M21 10l4-1'/>",
            "Appearance"=>"<path d='M10 4l6 4 6-4 8 8-6 5-3-3 3 15H8l3-15-3 3-6-5z'/>",
            "Mail"=>"<path d='M3 7h26v19H3zM3 8l13 11L29 8M3 26l8-10M29 26l-8-10'/>",
            "Social"=>"<circle cx='12' cy='10' r='4'/><circle cx='23' cy='12' r='3'/><path d='M3 28v-5c0-8 18-8 18 0v5M23 19c6 0 7 3 7 8'/>",
            "Settings"=>"<path d='M13 2h6l1 5 4 2 5-1 3 5-4 4v4l-4 4-5-1-3 4-5-3-5 1-3-5 2-5-2-5 5-3 1-6z'/><circle cx='16' cy='16' r='5'/>",
            "Chat"=>"<path d='M3 5h26v18H13l-8 6v-6H3zM8 11h16M8 17h11'/>",
            "Retry"=>"<path d='M26 10a11 11 0 1 0 1 11M26 3v8h-8'/>",
            "Interact"=>"<path d='M5 29V15l6-4 5 5V4c0-3 4-3 4 0v10c8-1 9 3 8 9l-2 6z'/>",
            _=>"<path d='M16 2l14 14-14 14L2 16zM16 9v10M16 23h.1'/>"};
        var image=new Image();image.LoadSvgFromString("<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'><g fill='none' stroke='#d4dbff' stroke-width='1.7' stroke-linejoin='round' stroke-linecap='round'>"+path+"</g></svg>",2);
        t=ImageTexture.CreateFromImage(image);Cache[key]=t;return t;
    }
}
