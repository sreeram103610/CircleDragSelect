//
//  KSRegistration.h
//  KeystoneRegistration.framework
//
//  Created by John Grabowski 2/20/08.
//  Copyright 2008 Google Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <Security/Authorization.h>

@class KSActionProcessor;

typedef enum {
  kKSPathExistenceChecker,
  kKSLSExistenceChecker,
  kKSSpotlightExistenceChecker,
} KSExistenceCheckerType;

typedef enum {
  kKSRegistrationUserTicket,
  kKSRegistrationSystemTicket,
  kKSRegistrationDontKnowWhatKindOfTicket,
} KSRegistrationTicketType;

// Parameter dictionary keys, used for -registerWithParameters,
// -promoteWithParameters, and -ticketInfo.
// The values for these keys should be NSStrings, except for
// the existence checker type, which should be a KSExistenceCheckerType
// wrapped in an NSNumber, and the trusted tester token preservation flag,
// which should be an NSNumber wrapped BOOL.
extern NSString *KSRegistrationVersionKey;
extern NSString *KSRegistrationExistenceCheckerTypeKey;        // NSNumber
extern NSString *KSRegistrationExistenceCheckerStringKey;
extern NSString *KSRegistrationServerURLStringKey;
extern NSString *KSRegistrationPreserveTrustedTesterTokenKey;  // NSNumber
extern NSString *KSRegistrationTrustedTesterTokenKey;  // read-only
extern NSString *KSRegistrationTagKey;
extern NSString *KSRegistrationTagPathKey;
extern NSString *KSRegistrationTagKeyKey;
extern NSString *KSRegistrationBrandPathKey;
extern NSString *KSRegistrationBrandKeyKey;
extern NSString *KSRegistrationVersionPathKey;
extern NSString *KSRegistrationVersionKeyKey;

// Notification-related constants.

// Name of the notification posted when an async install and/or
// register completes.  See additional comments below.
extern NSString *KSRegistrationDidCompleteNotification;

// Name of the notification posted when the Agent's "check for updates"
// UI has been dsplayed.  This only gets posted for optional installs,
// and won't get called for silent installs.
extern NSString *KSRegistrationUpdateUIDisplayedNotification;

// Name of the notification posted when -promoteWithVersion:...
// completes.  Info dictionary contains a number-wrapped BOOL
// under KSRegistrationStatusKey and the authorizated process's output
// under KSRegistrationPromotionRawResultsKey.
extern NSString *KSRegistrationPromotionDidCompleteNotification;


// ----------------------------------------------------------------------------

// Name of the notification posted when an async check for available
// updates completes.
extern NSString *KSRegistrationCheckForUpdateNotification;

// Key for userInfo dictionary in the
// KSRegistrationCheckForUpdateNotification.  Value for this key is
// always a BOOL encoded in an NSNumber.
extern NSString *KSRegistrationStatusKey;

// Key for userInfo dictionary in the
// KSRegistrationCheckForUpdateNotification.  Value for this key is a
// version encoded in an NSString (e.g. @"1.0.2.10").  This key may
// not be present for all types of updates; for example, silent
// updates don't tell the client (us) the new version.
extern NSString *KSRegistrationVersionKey;

// Key for userInfo dictionary in the KSRegistrationCheckForUpdateNotification.
// Value for this key is a BOOL (wrapped in an NSNumber).  If it is YES,
// then -checkForUpdate could not be completed.
extern NSString *KSRegistrationUpdateCheckErrorKey;

// Key for userInfo dictionary in the KSRegistrationCheckForUpdateNotification.
// Value for this key is an NSString of the raw results emitted from
// Keystone.  Depending on the format of this string would be a bad idea
// because future and past versions of Keystone / Cocoa may cause it to
// have unpredictable values; but it can be handy for debugging.
extern NSString *KSRegistrationUpdateCheckRawResultsKey;

// Key for userInfo dictionary in the
// KSRegistrationPromotionDidCompleteNotification. Value for this key is an
// NSString of the raw results emitted from a command run with authorization.
extern NSString *KSRegistrationPromotionRawResultsKey;

// ----------------------------------------------------------------------------

// Name of the notification posted when an explicit update check
// request has completed.  Note that, on success, it may never get
// sent (e.g. if called from Foo.app, and if Foo.app is
// killed/restarted as part of an upgrade, you'll die before it
// completes).
extern NSString *KSRegistrationStartUpdateNotification;

// Key for userInfo dictionary in the
// KSRegistrationStartUpdateNotification.  Value is a BOOL (encoded as
// an NSNumber) stating if the update check was successful or not.
extern NSString *KSUpdateCheckSuccessfulKey;

// Key for userInfo dictionary in the
// KSRegistrationStartUpdateNotification.  Value is an int (encoded as
// an NSNumber) whch states how many products were successfully
// installed (likely 0 or 1).
extern NSString *KSUpdateCheckSuccessfullyInstalledKey;

// BOOL encoded as an NSNumber.  Set to YES if the user decided to
// update later using the Agent's UI.
extern NSString *KSUpdateCheckUpdateLaterKey;


// Other constants.

// Constant for -registerWithVersion:...tag: to remove an existing tag
// from the ticket.
extern NSString *KSRegistrationRemoveExistingTag;

// Constant for -registerWithVersion:...tag: to preserve an existing
// tag in the ticket.  Do not use with -registerWithParameters.  Preservation
// is the default for that call.
#define KSRegistrationPreserveExistingTag nil


// KSRegistration
//
// This is the main interface a drag install (non-root) Keystone
// client will use.  Typically, a drag-installed application will link
// with KeystoneRegistration.framework.  On launch, the application
// can then register itself with Keystone (-[KSRegistration
// registerWithVersion::::], which installs Keystone if needed, to
// enable software updates.
//
// It is fine for an application to unconditionally
// -registerWithVersion:::: on launch.
//
// Example use:
//
//    KSRegistration *registration = [KSRegistration registrationWithProductID:...];
//    if ([registration registerWithVersion: .... ] == NO) {
//      NSLog(@"Registration of Keystone ticket failed");
//    }
//  }
//
// In addition to installation, this class allows products to inform Keystone
// when they are 'active', which Keystone will then report to the server so that
// we can calculate '7-day actives' for each product. See the
// -setActive method below for more details.
//
@interface KSRegistration : NSObject {
 @private
  // The root directory in which to install Keystone, usually a home
  // directory.  This typically won't be changed other than unit
  // testing.
  NSString *installRoot_;

  // The first place in which we look for an installed Keystone when
  // determining if it is already installed.  The 2nd place to look is
  // "installRoot_".  We do not install anything in here.
  NSString *firstSearchRoot_;

  // The bundle which contains the Keystone package we are to install.
  NSBundle *bundle_;

  // For testing register we don't want to klobber a user's real store.
  // Private APIs for testing let us change this.
  NSString *storePath_;

  // If NO, do not launch processes (add --no-proclaunch on install).
  // Only used for testing.
  BOOL noProcLaunch_;

  // YES if we should force install (add --force to the install script).
  // Only used for unit testing.
  BOOL doForce_;

  // YES if we should only install (and never register anything).
  // Only used for unit testing.
  BOOL installOnly_;

  // The product for this registration object.
  NSString *productID_;

  // How we keep track of async operations.
  KSActionProcessor *processor_;

  KSRegistrationTicketType ticketType_;
}

// Return an autoreleased registration object in which registration is
// async.
//  |productID| is unique for your product (GUID, or app bundleID)
+ (id)registrationWithProductID:(NSString *)productID;

// Returns YES or NO to tell if a Keystone is already installed.
- (BOOL)isInstalled;

// Register a product with Keystone, generating a ticket.
// Re-registering an existing ticket, even if nothing changes, is NOT
// an error.  (Re-registering an existing ticket with a new version is
// not, of course, an error).  This routine DOES make sure Keystone is
// already installed. On completion, a
// KSRegistrationDidCompleteNotification is posted.  The notification
// object is the KSRegistration itself.  The userInfo dictionary
// contains an NSNumber, YES or NO, which states if the register (and
// possible install) worked.  This NSNumber is indexed by
// KSRegistrationStatusKey.
//
// This routine does NOT implicitly call setActive.  If you wish
// for active information, call setActive explicitly.
//
// If there is already a system ticket, the user ticket is deleted and
// this operation is a no-op.  The KSRegistrationStatusKey in the
// notification userInfo is set to YES in this case.
//
// Briefly,
//  |version| is the version of the currently running app
//  |xctype| specifies the type of existence checker (to help detect,
//    e.g., drag-uninstalls)
//  |xc| is the string used for an existence check (for Path, it's the path)
//  |serverURLString| is a string which points to the server URL which
//    can update your product (has an Omaha server running).
// See the Keystone documentation for more details.
// Return YES if we could begin the registration process; NO on
// failure.
- (BOOL)registerWithVersion:(NSString *)version
       existenceCheckerType:(KSExistenceCheckerType)xctype
     existenceCheckerString:(NSString *)xc
            serverURLString:(NSString *)serverURLString;

// Same as register, but allows the caller to preserve the trusted tester
// token if desired (and if already in the ticket).  Otherwise, the
// token is lost on register (if already there).
- (BOOL)registerWithVersion:(NSString *)version
       existenceCheckerType:(KSExistenceCheckerType)xctype
     existenceCheckerString:(NSString *)xc
            serverURLString:(NSString *)serverURLString
            preserveTTToken:(BOOL)preserveToken;

// Another register variant which allows the caller to preserve the
// trusted tester token if desired (and if already in the ticket).
// Otherwise, the token is lost on register (if already there).  Also,
// a Tag can be supplied, which will be added to the ticket.  The Tag
// is sent to the Omaha server when doing an update check.
// The Tag is a non-empty string.
// Pass KSRegistrationRemoveExistingTag for |tag| to remove the tag from the
//      ticket (if it exists).
// Pass KSRegistrationPreserveExistingTag for |tag| to preserve the tag without
//      changing it.  This is the default behavior for the non-tag variants
//      of the -registerWithVersion:... calls.
- (BOOL)registerWithVersion:(NSString *)version
       existenceCheckerType:(KSExistenceCheckerType)xctype
     existenceCheckerString:(NSString *)xc
            serverURLString:(NSString *)serverURLString
            preserveTTToken:(BOOL)preserveToken
                        tag:(NSString *)tag;

// Registers a product with Keystone, generating a ticket.
// Create a dictionary using the KSRegistation* keys declared at the
// top of the file.
// The version, existence checker type and string, and the server url string
// are required.
// The trusted tester token preservation value will default to NO if not
// supplied.
// This is the only way you can have a tag path with your ticket (and
// any future registration parameters).
// The tag path obeys the same semantics as tag registering.  By
// default the tag will be preserved - you do not want to use
// KSRegistrationPreserveExistingTag. It's nil, and will generally
// give NSDictionary heartburn.  When removing the tag path / key, go
// ahead and use KSRegistrationRemoveExistingTag for the tag path
// keys.
// Use KSRegistrationRemoveExistingTag when removing brand code keys as well.
- (BOOL)registerWithParameters:(NSDictionary *)args;

// Register the application's ticket as a *system* ticket, possibly
// installing the registration's framework keystone as a system
// keystone.  It is the caller's responsibility to make sure that they
// believe the bits on disk can be trusted to run the Keystone
// install.py (and unpack the Keystone.tbz) from within the
// KeystoneRegistration.framework, with privileges.  The arguments are
// the same as with -registerWithParameters.  |authorization| should
// be a valid AuthoriationRef.  Returns NO if there were problems with
// the arguments.
//
// Note that applications that promote need to provide some kind of
// uninstall mechanism to remove their system ticket so that the
// system keystone can uninstall itself.
- (BOOL)promoteWithParameters:(NSDictionary *)args
                authorization:(AuthorizationRef)authorization;

// Unregister the application, removing its ticket from the ticketstore.
// It is not an error to unregister an app that doesn't have a ticket.
- (BOOL)unregister;

// Return the ProductID for this KSRegistration object.
- (NSString *)productID;

// Return the tag for the KSRegistration's product.  This is a sync call to
// to ksadmin.
//   Returns an empty string is there is no tag.
//   Returns nil if the tag could not be retrieved.
- (NSString *)tag;

// Return the brand code for the KSRegistration's product.  This is a
// sync call to to ksadmin.
//   Returns an empty string is there is no brand specified in the ticket.
//   Returns nil if the brand could not be retrieved.
- (NSString *)brand;

// Return the effective version for the KSRegistration's product.  This is a
// sync call to ksadmin.
//   Returns the value looked up by the versionPath/Tag.  If that is an invalid
//   combination, returns the ticket's version.
// Returns nil if the version could not be determined.
- (NSString *)effectiveVersion;

// Tells Keystone that this product has been 'active' within the last 24-hours.
// Keystone will upload this information to the server, and it can be used to
// calculate "7-day actives".
//
// If your application is left running for more than one day, it is your
// responsibility to call this method each day to inform Keystone that your app
// is still active. Otherwise, Keystone will only report that your app was
// active for one day.
- (void)setActive;

// Ask Keystone if updates are available for the productID passed into
// the initializer.  The result is posted as a
// KSRegistrationCheckForUpdateNotification; the NSNotification's
// userInfo contains an NSNumber, YES or NO, which tells if updates
// are available.  This NSNumber is indexed by key KSStatusKey.  The
// new version available is encoded as an NSString in the userInfo,
// keyed by KSRegistrationVersionKey.
// This call does NOT perform a download/install and does not bring up
// UI.  Applications that wish to check for updates on launch could
// call this.
- (void)checkForUpdate;

// Check for an update RIGHT NOW for this registration's productID.
// This launches a Keystone process which displays UI if an update is
// available.  It is expected that this be called from a menu option.
// This call is not normally needed by Keystone clients since the
// Keystone process will launch itself (and check) once a day anyway.
// Once the explicit update check has completed, a
// KSRegistrationStartUpdateNotification is posted.  Keys in the
// notification's userInfo include KSUpdateCheckSuccessfulKey and
// KSUpdateCheckSuccessfullyInstalledKey.  If an update check was
// possible but no updates are available, it is expected that
// KSUpdateCheckSuccessfulKey would be YES and
// KSUpdateCheckSuccessfullyInstalledKey would be 0.
- (void)startUpdate;

// This is a sync call to ksadmin which will return information about
// your ticket.  The keys and values for the returned dictionary match
// those used for -register/promoteWithParameters.
- (NSDictionary *)ticketInfo;

// Returns the kind of ticket the registration thinks it has.  This
// value gets set as a side effect of checking for updates.  If the
// current ticket type is kKSRegistrationDontKnowWhatKindOfTicket,
// a sync call to ksadmin will be made to determine the type.
- (KSRegistrationTicketType)ticketType;

@end


@interface KSRegistration (ObsoleteAPI)

// Replaced by +(id)registrationWithProductID:
// Also note all ops are now async.
+ (id)registration;
+ (id)asyncRegistration;

// ProductID now passed in to initializer
- (BOOL)registerWithProductID:(NSString *)productID
                      version:(NSString *)version
         existenceCheckerType:(KSExistenceCheckerType)xctype
       existenceCheckerString:(NSString *)xc
              serverURLString:(NSString *)serverURLString;

// Replaced by the argless versions, since productID is now passed to
// the initializer.
- (void)setActiveStatusForProductID:(NSString *)productID;

- (BOOL)promoteWithVersion:(NSString *)version
      existenceCheckerType:(KSExistenceCheckerType)xctype
    existenceCheckerString:(NSString *)xc
           serverURLString:(NSString *)serverURLString
           preserveTTToken:(BOOL)preserveToken
                       tag:(NSString *)tag
             authorization:(AuthorizationRef)authorization;

@end  // KSRegistration (ObsoleteAPI)
