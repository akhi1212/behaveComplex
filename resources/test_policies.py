from time import gmtime
from calendar import timegm

TEST_SHIPPED = {
  "id": "/anyMNO/TEST_SHIPPED",
  "policyModel": {
    "reference": {
      "id": "/anyMNO/TEST_SHIPPED",
      "version": 1,
      "tags": {
        "name": "TEST_SHIPPED"
      }
    },
    "definition": {
      "definitionV1": {
        "checkin": {
          "period": 5
        },
        "notification": {},
        "periodicNotification": {},
        "bootNotification": {},
        "deviceLock": {
          "features": [],
          "whitelistApps": [],
          "whitelistNumbers": [],
          "screenLock": None
        },
        "unlockPinTransition": None,
        "staleTransition": None,
        "releaseClient": False,
        "configMap": {
          "additionalProp1": "string",
          "additionalProp3": "string",
          "additionalProp2": "string"
        }
      }
    }
  },
  "deleted": False
}

TEST_LOCK = {
      "id": "/anyMNO/TEST_LOCK",
      "timestamp": timegm(gmtime()),
      "policyModel": {
        "reference": {
          "id": "/anyMNO/TEST_LOCK",
          "version": 1,
          "assignedTime": None,
          "tags": {
            "hidden": False,
            "name": "TEST_LOCK",
            "colourIndicator": ""
          }
        },
        "definition": {
          "definitionV1": {
            "checkin": {
              "period": 60
            },
            "notification": None,
            "alpsActionScheduling": {
              "delayInitialActivation": False,
              "activationWindow": None,
              "nonDismissible": True,
              "activationDuration": None,
              "repetitionInterval": None,
              "oncePerDay": False
            },
            "kgActionScheduling": {
              "delayInitialActivation": False,
              "nonDismissible": False,
              "activationDuration": None,
              "repetitionInterval": None,
              "oncePerDay": False
            },
            "bootNotification": None,
            "deviceLock": {
              "features": [],
              "whitelistApps": [],
              "whitelistNumbers": [],
              "screenLock": {
                "imageReference": "",
                "title": {
                  "localeValues": {},
                  "defaultValue": "TEST_LOCK"
                },
                "message": {
                  "localeValues": {},
                  "defaultValue": "TEST_LOCK"
                },
                "contacts": []
              }
            },
            "unlockPinTransition": None,
            "staleTransition": None,
            "releaseClient": False,
            "serverScheduledTransition": None,
            "knoxGuardMessage": None,
            "knoxGuardDismissibleScreenLock": None,
            "knoxGuardScreenLock": {
              "tel": None,
              "email": "nomail@trustonic.com",
              "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin non diam ipsum. Donec a erat "
                         "non diam ornare ornare quis ultrices erat. Donec ac justo nec est facilisis dapibus vel id "
                         "lectus. Vestibulum vehicula tincidunt purus, sed pretium elit tristique eu. Phasellus "
                         "consectetur nec libero nec pretium. Lorem ipsum dolor sit amet, consectetur cras. "
            }
          }
        }
      },
      "deleted": False
    }

TEST_UNLOCK = {
      "id": "/anyMNO/TEST_UNLOCK",
      "timestamp": timegm(gmtime()),
      "policyModel": {
        "reference": {
          "id": "/anyMNO/TEST_UNLOCK",
          "version": 1,
          "assignedTime": None,
          "tags": {
            "hidden": False,
            "name": "TEST_UNLOCK",
            "colourIndicator": "green-4"
          }
        },
        "definition": {
          "definitionV1": {
            "checkin": {
              "period": 10
            },
            "notification": {
              "localeValues": {},
              "defaultValue": "Unlock policy without restrictions",
              "fullScreen": True
            },
            "alpsActionScheduling": {
              "delayInitialActivation": False,
              "activationWindow": None,
              "nonDismissible": False,
              "activationDuration": None,
              "repetitionInterval": None,
              "oncePerDay": False
            },
            "kgActionScheduling": {
              "delayInitialActivation": False,
              "activationWindow": None,
              "nonDismissible": True,
              "activationDuration": None,
              "repetitionInterval": None,
              "oncePerDay": False
            },
            "bootNotification": None,
            "deviceLock": {
              "features": [],
              "whitelistApps": [],
              "whitelistNumbers": [],
              "screenLock": None
            },
            "unlockPinTransition": None,
            "staleTransition": None,
            "releaseClient": False,
            "serverScheduledTransition": None,
            "knoxGuardMessage": {
              "tel": "123123",
              "message": "Unlock policy without restrictions",
              "fullScreen": False
            },
            "knoxGuardDismissibleScreenLock": None,
            "knoxGuardScreenLock": None
          }
        }
      },
      "deleted": False
    }

TEST_MESSAGE = {
      "id": "/anyMNO/TEST_MESSAGE",
      "timestamp": timegm(gmtime()),
      "policyModel": {
        "reference": {
          "id": "/anyMNO/TEST_MESSAGE",
          "version": 1,
          "assignedTime": None,
          "tags": {
            "hidden": False,
            "name": "/TEST_MESSAGE",
            "colourIndicator": "green-4"
          }
        },
        "definition": {
          "definitionV1": {
            "checkin": {
              "period": 300
            },
            "notification": {
              "localeValues": {},
              "defaultValue": "POLICY TEST MESSAGE applied!",
              "fullScreen": True
            },
            "alpsActionScheduling": None,
            "kgActionScheduling": None,
            "bootNotification": None,
            "deviceLock": None,
            "unlockPinTransition": None,
            "staleTransition": None,
            "releaseClient": False,
            "serverScheduledTransition": None,
            "knoxGuardMessage": {
              "tel": "+189632541",
              "message": "POLICY TEST MESSAGE applied!",
              "fullScreen": True
            },
            "knoxGuardDismissibleScreenLock": None,
            "knoxGuardScreenLock": None
          }
        }
      },
      "deleted": False
    }

TEST_NOTIFICATION = {
      "id": "/anyMNO/TEST_NOTIFICATION",
      "timestamp": timegm(gmtime()),
      "policyModel": {
        "reference": {
          "id": "/anyMNO/TEST_NOTIFICATION",
          "version": 1,
          "assignedTime": None,
          "tags": {
            "hidden": "False",
            "name": "TEST_NOTIFICATION",
            "colourIndicator": ""
          }
        },
        "definition": {
          "definitionV1": {
            "checkin": {
              "period": 60
            },
            "notification": {
              "localeValues": {},
              "defaultValue": "POLICY TEST NOTIFICATION applied!",
              "fullScreen": False
            },
            "alpsActionScheduling": {
              "delayInitialActivation": True,
              "activationWindow": {
                "days": [
                  "MONDAY",
                  "TUESDAY",
                  "WEDNESDAY",
                  "THURSDAY",
                  "FRIDAY",
                  "SATURDAY",
                  "SUNDAY"
                ],
                "excludeHolidays": True,
                "start": 36000,
                "end": 79200
              },
              "nonDismissible": False,
              "activationDuration": None,
              "repetitionInterval": None,
              "oncePerDay": False
            },
            "kgActionScheduling": None,
            "bootNotification": None,
            "deviceLock": None,
            "unlockPinTransition": None,
            "staleTransition": None,
            "releaseClient": False,
            "serverScheduledTransition": None,
            "knoxGuardMessage": None,
            "knoxGuardDismissibleScreenLock": None,
            "knoxGuardScreenLock": None
          }
        }
      },
      "deleted": False
    }

TEST_BLINK = {
  "id": "/anyMNO/TEST_BLINK",
  "policyModel": {
    "reference": {
      "id": "/anyMNO/TEST_BLINK",
      "version": 1,
      "tags": {
        "name": "TEST_BLINK"
      }
    },
    "definition": {
      "definitionV1": {
        "checkin": {
          "period": 5
        },
        "notification": {},
        "periodicNotification": {},
        "bootNotification": {},
        "deviceLock": {
          "features": [],
          "whitelistApps": [],
          "whitelistNumbers": [],
          "screenLock": None
        },
        "unlockPinTransition": None,
        "staleTransition": None,
        "releaseClient": False,
        "knoxGuardDismissibleScreenLock": {
               "tel": "+189632541",
               "email": "nomail@trustonic.com",
               "interval": 60,
               "message": "POLICY TEST BLINK applied!",
               "temporaryDisablePeriod": None
             },
        "configMap": {
          "additionalProp1": "string",
          "additionalProp3": "string",
          "additionalProp2": "string"
        }
      }
    }
  },
  "deleted": False
}

TEST_RELEASE = {
      "id": "/anyMNO/TEST_RELEASE",
      "timestamp": timegm(gmtime()),
      "policyModel": {
        "reference": {
          "id": "/anyMNO/TEST_RELEASE",
          "version": 1,
          "assignedTime": None,
          "tags": {
            "hidden": "False",
            "name": "TEST_RELEASE",
            "colourIndicator": ""
          }
        },
        "definition": {
          "definitionV1": {
            "checkin": {
              "period": 60
            },
            "notification": None,
            "alpsActionScheduling": None,
            "kgActionScheduling": None,
            "bootNotification": None,
            "deviceLock": None,
            "unlockPinTransition": None,
            "staleTransition": None,
            "releaseClient": True,
            "serverScheduledTransition": None,
            "knoxGuardMessage": None,
            "knoxGuardDismissibleScreenLock": None,
            "knoxGuardScreenLock": None
          }
        }
      },
      "deleted": False
    }
