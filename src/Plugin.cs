using System;
using System.Collections.Generic;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using ServerSync;

namespace TameProtection
{
    [BepInPlugin(PluginGuid, PluginName, PluginVersion)]
    public class Plugin : BaseUnityPlugin
    {
        public const string PluginGuid = "com.n3bby.tameprotection";
        public const string PluginName = "TameProtection";
        public const string PluginVersion = "1.0.0";

        // ModRequired = false: a client without the mod is not kicked, it simply
        // does not receive the protection. Keeps 1.0.0's lenient behaviour.
        private static readonly ConfigSync ConfigSync = new(PluginGuid)
        {
            DisplayName = PluginName,
            CurrentVersion = PluginVersion,
            MinimumRequiredVersion = PluginVersion,
            ModRequired = false,
        };

        internal static ManualLogSource Log;
        internal static ConfigEntry<bool> ProtectTamedFromEnemies;
        internal static ConfigEntry<string> ProtectedPrefabs;
        internal static ConfigEntry<bool> DebugLogging;
        private static ConfigEntry<bool> _serverConfigLocked;

        private static readonly HashSet<string> PrefabFilter =
            new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        /// <summary>Bind a setting; synced ones are owned by the server.</summary>
        private ConfigEntry<T> Bind<T>(string group, string name, T value, string description,
                                       bool synced = true)
        {
            var entry = Config.Bind(group, name, value,
                new ConfigDescription(description + (synced
                    ? " [Synced with Server]"
                    : " [Not Synced with Server]")));
            ConfigSync.AddConfigEntry(entry).SynchronizedConfig = synced;
            return entry;
        }

        private void Awake()
        {
            Log = Logger;

            _serverConfigLocked = Bind(
                "General", "LockConfiguration", true,
                "Only server admins may change synced settings while connected to a server.");
            ConfigSync.AddLockingConfigEntry(_serverConfigLocked);

            ProtectTamedFromEnemies = Bind(
                "General", "ProtectTamedFromEnemies", true,
                "Wild creatures and tamed creatures no longer treat each other as enemies. " +
                "This is mutual: enemies will not target your tames, and your tames will not " +
                "start fights with enemies. Wild-vs-wild and tame-vs-tame are left untouched.");

            ProtectedPrefabs = Bind(
                "General", "ProtectedPrefabs", "",
                "Optional comma-separated creature prefab names to protect (e.g. Asksvin,Lox). " +
                "Leave empty to protect every tamed creature.");

            // Local diagnostics: every player decides for themselves.
            DebugLogging = Bind(
                "General", "DebugLogging", false,
                "Log every hostility check this mod suppresses. Very noisy; for testing only.",
                synced: false);

            RebuildFilter();
            ProtectedPrefabs.SettingChanged += (s, e) => RebuildFilter();

            new Harmony(PluginGuid).PatchAll();
            Log.LogInfo("[startup.ok] " + PluginName + " " + PluginVersion +
                        " (patching BaseAI.IsEnemy; config synced with server)");
        }

        private static void RebuildFilter()
        {
            PrefabFilter.Clear();
            var raw = ProtectedPrefabs.Value;
            if (string.IsNullOrEmpty(raw)) return;
            foreach (var part in raw.Split(','))
            {
                var name = part.Trim();
                if (name.Length > 0) PrefabFilter.Add(name);
            }
        }

        /// <summary>Prefab name without Unity's "(Clone)" suffix.</summary>
        internal static string PrefabName(Character c)
        {
            var n = c.gameObject.name;
            var i = n.IndexOf("(Clone)", StringComparison.Ordinal);
            return i >= 0 ? n.Substring(0, i) : n;
        }

        internal static bool IsProtected(Character tame)
        {
            return PrefabFilter.Count == 0 || PrefabFilter.Contains(PrefabName(tame));
        }
    }

    /// <summary>
    /// BaseAI.IsEnemy(Character, Character) is the single hostility check in the game;
    /// the instance overload compiles to `return BaseAI.IsEnemy(this.m_character, other)`,
    /// so patching the static one covers every caller.
    /// </summary>
    [HarmonyPatch(typeof(BaseAI), nameof(BaseAI.IsEnemy), new[] { typeof(Character), typeof(Character) })]
    internal static class Patch_BaseAI_IsEnemy
    {
        private static void Postfix(Character a, Character b, ref bool __result)
        {
            if (!__result) return;
            if (!Plugin.ProtectTamedFromEnemies.Value) return;
            if (a == null || b == null) return;

            var aTamed = a.IsTamed();
            var bTamed = b.IsTamed();
            // Both wild or both tame: leave vanilla behaviour alone.
            if (aTamed == bTamed) return;

            var tame = aTamed ? a : b;
            if (!Plugin.IsProtected(tame)) return;

            __result = false;
            if (Plugin.DebugLogging.Value)
                Plugin.Log.LogInfo("suppressed hostility: " +
                                   Plugin.PrefabName(a) + " <-> " + Plugin.PrefabName(b));
        }
    }
}
