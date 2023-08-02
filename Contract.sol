// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;


contract MyContract {

        address customer;
        address courier;
        uint256 orderAmount;
        uint256 storeAmount;
        uint256 courierAmount;
        bool isDelivered;
        bool isPaid;
        bool isPicked;
        address owner;


    constructor(address _customer, uint256 _orderAmount) {

        customer = _customer;
        orderAmount = _orderAmount;
        owner=msg.sender;
        isPaid=false;
        isPicked=false;

    }

    function transferFunds() external payable {

        storeAmount = (orderAmount * 80) / 100;
        courierAmount = (orderAmount * 20) / 100;
        isPaid=true;

    }

    function bindCourier(address _courier) external {
        courier = _courier;
        isPicked=true;
    }

    function confirmDelivery() external {
        isDelivered = true;
        payable(owner).transfer(storeAmount);
        payable(courier).transfer(courierAmount);
    }

    function getDeliveryStatus() public view returns (bool) {
        return isDelivered;
    }

    function getPaymentStatus() public view returns (bool) {
        return isPaid;
    }

    function getPickupStatus() public view returns (bool) {
        return isPicked;
    }

        function getCustomer() public view returns (address) {
        return customer;
    }

}





