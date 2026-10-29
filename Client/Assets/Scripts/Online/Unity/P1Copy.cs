using System.Collections.Generic;
using System.Globalization;
using Newtonsoft.Json;
using UnityEngine;

namespace NguMach.Client.P1
{
    public static class P1Copy
    {
        private static Dictionary<string, string> strings;
        public static string Get(string key, params object[] args)
        {
            if (strings == null)
            {
                var asset = Resources.Load<TextAsset>("Localization/p1_vi");
                strings = asset == null ? new Dictionary<string, string>() : JsonConvert.DeserializeObject<Dictionary<string, string>>(asset.text);
            }
            string value;
            if (!strings.TryGetValue(key, out value)) return key;
            return args.Length == 0 ? value : string.Format(CultureInfo.GetCultureInfo("vi-VN"), value, args);
        }
    }
}
