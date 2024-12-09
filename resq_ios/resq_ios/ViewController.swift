//
//  ViewController.swift
//  resq_ios
//
//  Created by JJ Choi on 11/13/24.
//


import UIKit

class ViewController: UIViewController {

    //Button make
    let callButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Call 119", for: .normal)
        button.backgroundColor = .systemRed
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 50 // Initially circular
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()

    //Animation like dis
    var buttonTopConstraint: NSLayoutConstraint!
    var buttonCenterXConstraint: NSLayoutConstraint!
    var buttonWidthConstraint: NSLayoutConstraint!
    var buttonHeightConstraint: NSLayoutConstraint!

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .white
        setupCallButton()
    }

    
    private func setupCallButton() {
        //Add the button to the view
        view.addSubview(callButton)

        //Set initial constraints
        buttonTopConstraint = callButton.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        buttonCenterXConstraint = callButton.centerXAnchor.constraint(equalTo: view.centerXAnchor)
        buttonWidthConstraint = callButton.widthAnchor.constraint(equalToConstant: 100)
        buttonHeightConstraint = callButton.heightAnchor.constraint(equalToConstant: 100)

        NSLayoutConstraint.activate([
            buttonTopConstraint,
            buttonCenterXConstraint,
            buttonWidthConstraint,
            buttonHeightConstraint
        ])

        // Add tap action for animation
        callButton.addTarget(self, action: #selector(animateCallButton), for: .touchUpInside)
    }

    @objc private func animateCallButton() {
        // Update constraints for the new position and size
        buttonTopConstraint.isActive = false
        buttonTopConstraint = callButton.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20)
        buttonCenterXConstraint.isActive = false
        buttonCenterXConstraint = callButton.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -20)
        buttonWidthConstraint.constant = 150
        buttonHeightConstraint.constant = 50

        // Animate the changes
        UIView.animate(withDuration: 0.5, delay: 0, options: [.curveEaseInOut]) {
            self.callButton.layer.cornerRadius = 25 // Morph into a rounded rectangle
            self.view.layoutIfNeeded()
        }
    }
}
