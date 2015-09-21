require 'spec_helper'
describe 'devman' do

  context 'with defaults for all parameters' do
    it { should contain_class('devman') }
  end
end
