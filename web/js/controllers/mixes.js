(function() {


  'use strict';


  angular.module('mixMaestroApp').controller('MixesCtrl', ['$scope', '$http', '$timeout', '$ionicSideMenuDelegate', function($scope, $http, $timeout, $ionicSideMenuDelegate) {


    var pollTimeout;


    var getMixes = function() {
      cancelMixesPoll();
      $http.get('/auxes')
        .success(function(data) {
          $scope.mixes = [];
          angular.forEach(data, function(value, key) {
            value.id = key;
            $scope.mixes.push(value);
          });
        })
        .error(function() {
          delete $scope.mixes;
        })
        .finally(function() {
          scheduleMixesPoll(60 * 1000);
        });
    }


    var scheduleMixesPoll = function(delay) {
      pollTimeout = $timeout(getMixes, delay);
    };


    var cancelMixesPoll = function() {
      $timeout.cancel(pollTimeout);
    };


    $scope.$on('$destroy', cancelMixesPoll);


    getMixes();


    $timeout($ionicSideMenuDelegate.toggleLeft);


  }]);


}());