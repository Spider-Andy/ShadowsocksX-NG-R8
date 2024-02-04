//
//  StatusItemView.swift
//  ClashX
//
//  Created by CYC on 2018/6/23.
//  Copyright © 2018年 yichengchen. All rights reserved.
//

import AppKit
import Foundation
//import RxCocoa
//import RxSwift

open class StatusItemView: NSView {
    @IBOutlet var imageView: NSImageView!

    @IBOutlet var uploadSpeedLabel: NSTextField!
    @IBOutlet var downloadSpeedLabel: NSTextField!
    @IBOutlet var speedContainerView: NSView!

    var up: Double = 0
    var down: Double = 0
    static var statusItem: NSStatusItem!
    static func create() -> StatusItemView {
        return create(statusItem: NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength))
    }
    
    static func create(statusItem: NSStatusItem?) -> StatusItemView {
        self.statusItem = statusItem
        var topLevelObjects: NSArray?
        if Bundle.main.loadNibNamed("StatusItemView", owner: self, topLevelObjects: &topLevelObjects) {
            let view = (topLevelObjects!.first(where: { $0 is NSView }) as? StatusItemView)!
            view.setupView()
            view.imageView.image = NSImage(named: "menu_icon")!
            view.imageView.image?.isTemplate = true

            if let button = statusItem?.button {
                button.addSubview(view)
                button.imagePosition = .imageOverlaps
            }
            view.updateViewStatus(enableProxy: false)
            return view
        }
        return NSView() as! StatusItemView
    }
    
    func setMenu(menu: NSMenu){
        StatusItemView.statusItem.menu = menu
    }

    func setupView() {
        uploadSpeedLabel.textColor = NSColor.labelColor
        downloadSpeedLabel.textColor = NSColor.labelColor
    }

    func updateSize(width: CGFloat) {
        frame = CGRect(x: 0, y: 0, width: width, height: 22)
        StatusItemView.statusItem.length = width
    }

    func updateViewStatus(enableProxy: Bool) {
        if enableProxy {
//            imageView.contentTintColor = NSColor.labelColor
        } else {
            // imageView.contentTintColor = NSColor.labelColor.withSystemEffect(.disabled)
        }
    }

    func updateSpeedLabel(up: Int, down: Int) {
        updateSpeedLabel(up: Double(up), down: Double(down))
    }
    func updateSpeedLabel(up: Double, down: Double) {
        guard !speedContainerView.isHidden else { return }
        if up != self.up {
            uploadSpeedLabel.stringValue = SpeedTools.formatRateData(Float(up)) + "↑"
            self.up = up
        }
        if down != self.down {
            downloadSpeedLabel.stringValue = SpeedTools.formatRateData(Float(down)) + "↓"
            self.down = down
        }
    }

    func showSpeedContainer(show: Bool) {
        speedContainerView.isHidden = !show
        if show {
            StatusItemView.statusItem.length = 80
        } else {
            StatusItemView.statusItem.length = 24
        }
    }
    
    func updateStatusItemUI() {
        let defaults = UserDefaults.standard
        let mode = defaults.string(forKey: USERDEFAULTS_SHADOWSOCKS_RUNNING_MODE)
        if defaults.bool(forKey: USERDEFAULTS_SHADOWSOCKS_ON) {
            if mode == "auto" {
                self.imageView.image = NSImage(named: "menu_icon_pac")!
            } else if mode == "global" {
                self.imageView.image = NSImage(named: "menu_icon_global")!
            } else if mode == "manual" {
                self.imageView.image = NSImage(named: "menu_icon_manual")!
            } else if mode == "whiteList" {
                if UserDefaults.standard.string(forKey: USERDEFAULTS_ACL_FILE_NAME)! == "chn.acl" {
                    self.imageView.image = NSImage(named: "menu_icon_white")!
                } else {
                    self.imageView.image = NSImage(named: "menu_icon_acl")!
                }
            } else {
                self.imageView.image = NSImage(named: "menu_icon")!
            }
        } else {
            self.imageView.image = NSImage(named: "menu_icon_disabled")!
        }
        self.imageView.image?.isTemplate = true
    }
    
}
