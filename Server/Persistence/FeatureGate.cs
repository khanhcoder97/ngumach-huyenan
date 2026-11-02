// QR-01 — Feature gate for Server Persistence module with configuration management.
// Owner: QODER Remote Persistence — Issue #79 (Work Order 11).

using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;

namespace NguMach.Server.Persistence
{
    /// <summary>
    /// Feature gate controlling Server Persistence availability and behavior.
    /// Default: OFF as required by Work Order 11.
    /// </summary>
    public interface IFeatureGate : IDisposable
    {
        /// <summary>Current enabled state.</summary>
        bool IsEnabled { get; }

        /// <summary>Toggle feature on/off based on configuration.</summary>
        Task ToggleAsync(bool enable);

        /// <summary>Check if specific sub-feature is available.</summary>
        bool CanUseFeature(FeatureName feature);

        /// <summary>Get current feature version.</summary>
        string Version { get; }
    }

    public enum FeatureName
    {
        DatabasePersistence,
        AtomicMutations,
        CrashRecovery,
        OutboxPattern,
        LedgerTracking
    }

    /// <summary>Implements feature gate with environment/config support.</summary>
    internal sealed class FeatureGateImpl : IFeatureGate
    {
        private readonly IConfiguration? _config;
        private bool _isEnabled;
        private DateTime _lastStateChanged;
        private readonly object _lock = new();

        public const string ConfigKey = "qoderm_remote_persistence_enabled";
        public string Version => "1.0.0-alpha";

        public bool IsEnabled 
        { 
            get => _isEnabled;
            set
            {
                lock (_lock)
                {
                    _isEnabled = value;
                    _lastStateChanged = DateTime.UtcNow;
                }
            }
        }

        public FeatureGateImpl(IConfiguration? config = null)
        {
            _config = config;
            InitializeFromConfig();
        }

        private void InitializeFromConfig()
        {
            if (_config != null && bool.TryParse(_config[ConfigKey], out var parsed))
            {
                IsEnabled = parsed;
            }
            else
            {
                // Default OFF as required
                IsEnabled = false;
            }
        }

        public async Task ToggleAsync(bool enable)
        {
            await Task.Run(() =>
            {
                IsEnabled = enable;
                
                if (_config != null)
                {
                    _config[ConfigKey] = enable.ToString().ToLowerInvariant();
                }
            });
        }

        public bool CanUseFeature(FeatureName feature)
        {
            return IsEnabled && DateTime.UtcNow - _lastStateChanged > TimeSpan.FromMinutes(5); // Safety cooldown
        }

        public void Dispose()
        {
            // Cleanup resources if needed
        }
    }

    /// <summary>Extension methods for feature gate usage.</summary>
    public static class FeatureGateExtensions
    {
        /// <summary>Execute action only if feature is enabled.</summary>
        public static async Task ExecuteIfEnabledAsync<T>(this IFeatureGate gate, Func<Task<T>> action, T defaultValue)
        {
            if (!gate.IsEnabled)
                return;

            await action();
        }

        /// <summary>Throw exception if feature is disabled.</summary>
        public static void RequireEnabled(this IFeatureGate gate, FeatureName feature)
        {
            if (!gate.CanUseFeature(feature))
                throw new InvalidOperationException($"Feature '{feature}' is currently disabled");
        }

        /// <summary>Create feature gate with default configuration source.</summary>
        public static IFeatureGate CreateDefaultFeatureGate()
        {
            var configBuilder = new ConfigurationBuilder()
                .AddEnvironmentVariables("QR_")
                .AddUserSecrets(typeof(FeatureGateImpl).Assembly);

            var config = configBuilder.Build();
            return new FeatureGateImpl(config);
        }
    }
}
