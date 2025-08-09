# diagnostic_monitor.py

import time
import threading

class QDiagnosticMonitor:
    def __init__(self):
        self.status = {
            'ml_engine':              {'active': False, 'last_ping': None, 'error': None},
            'trade_recommender':      {'active': False, 'last_ping': None, 'error': None},
            'exit_strategy':          {'active': False, 'last_ping': None, 'error': None},
            'diagnostic_monitor':     {'active': False, 'last_ping': None, 'error': None},
            'pattern_memory_engine':  {'active': False, 'last_ping': None, 'error': None},
            'portfolio_tracker':      {'active': False, 'last_ping': None, 'error': None},
            'pattern_discovery':      {'active': False, 'last_ping': None, 'error': None},
            'confidence_monitor':     {'active': False, 'last_ping': None, 'error': None},
            'contact_event_evaluator':{'active': False, 'last_ping': None, 'error': None},
            'alerts':                 {'active': False, 'last_ping': None, 'error': None},
            'price_feed':             {'active': False, 'last_ping': None, 'error': None},
            'settings_store':         {'active': False, 'last_ping': None, 'error': None},
        }
        self.lock = threading.Lock()

    def ping(self, module_name):
        with self.lock:
            if module_name in self.status:
                self.status[module_name]['active'] = True
                self.status[module_name]['last_ping'] = time.strftime("%H:%M:%S")
                self.status[module_name]['error'] = None
                print(f"✅ PING: {module_name} at {self.status[module_name]['last_ping']}")

    def report_error(self, module_name, error_message):
        with self.lock:
            if module_name in self.status:
                self.status[module_name]['active'] = False
                self.status[module_name]['error'] = error_message

    def get_status(self):
        with self.lock:
            return self.status.copy()

    def get_all_module_status(self):
        with self.lock:
            return self.status.copy()

# Global instance (shared across system)
diagnostic_monitor = QDiagnosticMonitor()

# Optional helper function used by ML Engine
def track_module_impact(module_name, success):
    if success:
        diagnostic_monitor.ping(module_name)
    else:
        diagnostic_monitor.report_error(module_name, "Execution failed")

