/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUIContainer.h"
#import "MGConst.h"

@interface PyMainWindow : PyGUIContainer {}
// Navigation
- (void)selectNextView;
- (void)selectPreviousView;
- (NSInteger)currentPaneIndex;
- (void)setCurrentPaneIndex:(NSInteger)index;
- (NSInteger)paneCount;
- (NSString *)paneLabelAtIndex:(NSInteger)index;
- (NSInteger)paneTypeAtIndex:(NSInteger)index;
- (void)showPaneOfType:(NSInteger)paneType;
- (void)closePaneAtIndex:(NSInteger)index;
- (void)movePaneAtIndex:(NSInteger)paneIndex toIndex:(NSInteger)destIndex;
- (void)newTab;
- (void)showAccount;
- (void)navigateBack;
- (void)jumpToAccount;

// Item Management
- (void)deleteItem;
- (void)duplicateItem;
- (void)editItem;
- (void)makeScheduleFromSelected;
- (void)moveDown;
- (void)moveUp;
- (void)newGroup;
- (void)newItem;

// Other
- (NSString *)statusLine;
@end